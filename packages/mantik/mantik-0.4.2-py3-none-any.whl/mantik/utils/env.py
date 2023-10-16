import contextlib
import logging
import os
import typing as t

logger = logging.getLogger(__name__)


def get_required_env_var(name: str) -> str:
    """Return a required environment variable.

    Parameter
    ---------
    name : str
        Name of the environment variable.

    Raises
    ------
    NameError
        If the environment variable is unset.

    Returns
    -------
    str
        The value of the environment variable.


    """
    value = os.getenv(name)
    if value is None:
        raise NameError(f"Environment variable '{name}' not set")
    return value


def get_optional_env_var(
    name: str, default: t.Optional[str] = None
) -> t.Optional[str]:
    """Return an optional environment variable.

    Parameter
    ---------
    name : str
        Name of the environment variable.
    default : str, optional
        The default to return

    Returns
    -------
    str or None
        The value of the environment variable.


    """
    value = os.getenv(name, default=default)
    if value is None:
        logger.debug("Optional environment variable %s not set", name)
    return value


@contextlib.contextmanager
def env_vars_set(env_vars: t.Dict[str, t.Any]) -> None:
    """Set the given environment variables and unset afterwards.

    Parameters
    ----------
    env_vars : dict
        Environment variables and values to set.

    Notes
    -----
    All environment variables that were previously set to another value will
    be reset to the initial value afterwards.

    """
    set_env_vars(env_vars)
    yield
    unset_env_vars(env_vars.keys())


def set_env_vars(env_vars: t.Dict[str, t.Any]) -> None:
    """Set given environment variables.

    Parameters
    ----------
    env_vars : dict
        Environment variables and values to set.

    """
    logger.debug("Setting environment variables %s", env_vars)
    for key, value in env_vars.items():
        os.environ[key] = value


def unset_env_vars(env_vars: t.Iterable[str]) -> None:
    """Unset given environment variables.

    Parameters
    ----------
    env_vars : iterable
        Environment variables to be unset.

    """
    logger.debug("Unsetting environment variables %s", env_vars)
    for key in env_vars:
        try:
            os.environ.pop(key)
        except KeyError:
            # KeyError is raised if variable is already unset.
            pass
