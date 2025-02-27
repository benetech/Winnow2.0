import logging
import os
from typing import Callable

from cached_property import cached_property

from db import Database
from template_support.file_storage import FileStorage, LocalFileStorage
from winnow import remote
from winnow.config import Config
from winnow.remote import RemoteRepository
from winnow.remote.connect import RepoConnector, DatabaseConnector, ReprConnector
from winnow.remote.repository_dao import RepoDAO, RemoteRepoDatabaseDAO, RemoteRepoCsvDAO
from winnow.security import SecureStorage
from winnow.storage.db_result_storage import DBResultStorage
from winnow.storage.remote_signature_dao import (
    RemoteSignatureDatabaseDAO,
    RemoteSignatureReprDAO,
    RemoteSignatureDAOType,
)
from winnow.storage.repr_storage import ReprStorage
from winnow.storage.repr_utils import path_resolver
from winnow.utils.repr import reprkey_resolver, repr_storage_factory

logger = logging.getLogger(__name__)


class PipelineContext:
    """Pipeline components created and wired consistently according to the pipeline Config."""

    def __init__(self, config: Config):
        """Create pipeline context."""
        self._config = config

    @cached_property
    def config(self) -> Config:
        """Get pipeline config."""
        return self._config

    @cached_property
    def repr_storage(self) -> ReprStorage:
        """Get representation storage."""
        return ReprStorage(
            directory=self.config.repr.directory,
            storage_factory=repr_storage_factory(self.config),
        )

    @cached_property
    def database(self) -> Database:
        """Get result database."""
        database = Database(uri=self.config.database.uri)
        database.create_tables()
        return database

    @cached_property
    def reprkey(self) -> Callable:
        """Get representation key getter."""
        return reprkey_resolver(self.config)

    @cached_property
    def storepath(self) -> Callable:
        """Get a function to convert absolute file paths to storage root-relative paths."""
        return path_resolver(self.config.sources.root)

    @cached_property
    def result_storage(self) -> DBResultStorage:
        """Get database result storage."""
        return DBResultStorage(database=self.database)

    @cached_property
    def remote_signature_dao(self) -> RemoteSignatureDAOType:
        """Get remote signature DAO depending on the config."""
        if self.config.database.use:
            return RemoteSignatureDatabaseDAO(self.database)
        storage_root = os.path.join(self.config.repr.directory, "remote_signatures")
        return RemoteSignatureReprDAO(root_directory=storage_root, output_directory=self.config.repr.directory)

    @cached_property
    def repository_dao(self) -> RepoDAO:
        """Get repository Data-Access-Object."""
        if self.config.database.use:
            return RemoteRepoDatabaseDAO(database=self.database, secret_storage=self.secure_storage)
        return RemoteRepoCsvDAO(
            csv_file_path=os.path.join(self.config.repr.directory, "repositories.csv"),
            secret_storage=self.secure_storage,
        )

    @cached_property
    def secure_storage(self) -> SecureStorage:
        """Get secured credentials storage."""
        return SecureStorage(path=self.config.repr.directory, master_key_path=self.config.security.master_key_path)

    @cached_property
    def pretrained_model(self):
        """Load default model."""
        from winnow.feature_extraction import default_model_path, load_featurizer

        model_path = default_model_path(self.config.proc.pretrained_model_local_path)
        logger.info("Loading pretrained model from: %s", model_path)
        return load_featurizer(model_path)

    @cached_property
    def template_loader(self):
        """Get template loader."""
        from winnow.search_engine.template_loading import TemplateLoader

        return TemplateLoader(
            pretrained_model=self.pretrained_model,
            extensions=self.config.templates.extensions,
        )

    def make_connector(self, repo: RemoteRepository) -> RepoConnector:
        """Get remote repository connector."""
        client = remote.make_client(repo)
        if self.config.database.use:
            return DatabaseConnector(repo_name=repo.name, database=self.database, repo_client=client)
        return ReprConnector(
            repository_name=repo.name,
            remote_signature_dao=self.remote_signature_dao,
            signature_storage=self.repr_storage.signature,
            repo_client=client,
        )

    @cached_property
    def file_storage(self) -> FileStorage:
        """Create file storage for template examples."""
        return LocalFileStorage(directory=self.config.file_storage.directory)
