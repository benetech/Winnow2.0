import React from "react";
import clsx from "clsx";
import PropTypes from "prop-types";
import { makeStyles } from "@material-ui/styles";
import AttributeText from "../../../common/components/AttributeText";

const useStyles = makeStyles((theme) => ({
  hashContainer: {
    flexGrow: 1,
    flexShrink: 1,
    display: "flex",
    alignItems: "center",
    minWidth: 0,
  },
  iconContainer: {
    backgroundColor: theme.palette.primary.main,
    width: theme.spacing(4.5),
    height: theme.spacing(4.5),
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    borderRadius: theme.spacing(0.5),
    marginRight: theme.spacing(3),
    flexShrink: 0,
  },
  icon: {
    color: theme.palette.primary.contrastText,
    width: theme.spacing(3.5),
    height: theme.spacing(3.5),
  },
  attribute: {
    minWidth: 0,
  },
}));

function MainAttribute(props) {
  const { name, value, icon: Icon, highlight, className, ...other } = props;
  const classes = useStyles();

  return (
    <div className={clsx(classes.hashContainer, className)} {...other}>
      <div className={classes.iconContainer}>
        <Icon className={classes.icon} />
      </div>
      <AttributeText
        name={name}
        value={value}
        highlighted={highlight}
        variant="title"
        ellipsis
        className={classes.attribute}
      />
    </div>
  );
}

MainAttribute.propTypes = {
  /**
   * Attribute name.
   */
  name: PropTypes.string.isRequired,
  /**
   * Attribute value.
   */
  value: PropTypes.string.isRequired,
  /**
   * Highlight substring.
   */
  highlight: PropTypes.string,
  /**
   * Icon element type.
   */
  icon: PropTypes.elementType.isRequired,
  className: PropTypes.string,
};

export default MainAttribute;
