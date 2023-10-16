import logging
import typing as t

import mantik.unicore.exceptions as exceptions

logger = logging.getLogger(__name__)


def get_required_config_value(
    name: str, value_type: t.Type, config: t.Dict
) -> t.Any:
    """Get a required config value.

    Parameters
    ----------
    name : str
        Name of the config value.
    value_type : type
        Python type that the value is expected to have.
        Value will be cast to that type.
    config : t.Dict
        The config to read from.

    Raises
    ------
    ValueError
        If the config value is not present in the config.

    Returns
    -------
    Any
        The value from the config cast as `value_type`.

    """
    if name not in config:
        raise exceptions.ConfigValidationError(
            f"Config is missing entry for key {name!r}"
        )
    return _get_config_value(name=name, value_type=value_type, config=config)


def get_optional_config_value(
    name: str,
    value_type: t.Union[t.Type, t.Callable],
    config: t.Dict,
    default: t.Optional[t.Any] = None,
) -> t.Any:
    """Get an optional config value.

    Parameters
    ----------
    name : str
        Name of the config value.
    value_type : type or callable
        Python type that the value is expected to have.
        Value will be cast to that type.
    config : t.Dict
        The config to read from.
    default : t.Any, default=None
        The default value to return.

    Returns
    -------
    Any or None
        The value from the config cast as `value_type`, `None` if not present.

    """
    if name not in config:
        logger.debug(
            f"'{name}' not in configuration, using default value '{default}'."
        )
        return default
    return _get_config_value(name=name, value_type=value_type, config=config)


def _get_config_value(name: str, value_type: t.Type, config: t.Dict) -> t.Any:
    value = config[name]
    return _cast_type(name=name, value=value, value_type=value_type)


def _cast_type(name: str, value: str, value_type: t.Type) -> t.Any:
    try:
        return value_type(value)
    except ValueError as e:
        raise exceptions.ConfigValidationError(
            f"Config value for {name!r} has to be of type {value_type!r}"
        ) from e
