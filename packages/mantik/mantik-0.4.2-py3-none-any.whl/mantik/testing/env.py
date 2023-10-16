import os
import typing as t

import mantik.utils as utils


def assert_env_var(key: str, expected_value: t.Optional[str]) -> None:
    """Assert given environment variable has given value.

    Parameters
    ----------
    key : str
        Name of the variable.
    expected_value : str or None
        Expected value.

    Raises
    ------
    AssertionError
        If given environment variable
        does not have the expected value.

    """
    value = os.environ.get(key, None)
    assert value == expected_value


def assert_conflicting_mlflow_env_vars_not_set() -> None:
    """
    Assert that the conflicting environemnt variables of mlflow are not set.

    If `MLFLOW_TRACKING_USERNAME` or `MLFLOW_TRACKING_PASSWORD` are set, they
    are preferred by mlflow over `MLFLOW_TRACKING_TOKEN`, and thus, prevent
    the tracking from succeeding.

    """
    assert os.getenv(utils.mlflow.TRACKING_USERNAME_ENV_VAR) is None
    assert os.getenv(utils.mlflow.TRACKING_PASSWORD_ENV_VAR) is None


def assert_correct_tracking_token_env_var_set(expected_access_token) -> None:
    """
    Assert that the correct tracking token environment variable is set.
    """
    assert (
        os.getenv(utils.mlflow.TRACKING_TOKEN_ENV_VAR) == expected_access_token
    )
