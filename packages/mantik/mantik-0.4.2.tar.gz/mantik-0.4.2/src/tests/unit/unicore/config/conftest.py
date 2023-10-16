import os
import pathlib

import pytest

import mantik.unicore.config.core as core
import mantik.unicore.credentials as unicore_credentials
import mantik.utils as utils


@pytest.fixture
def required_config_env_vars():
    return {
        unicore_credentials._USERNAME_ENV_VAR: "test-user",
        unicore_credentials._PASSWORD_ENV_VAR: "test-password",
        core._PROJECT_ENV_VAR: "test-project",
    }


@pytest.fixture(scope="session")
def mlproject_path() -> pathlib.Path:
    return (
        pathlib.Path(__file__).parent
        / "../../../../../src/tests/resources/test-project"
    )


@pytest.fixture(scope="session")
def invalid_config_type() -> pathlib.Path:
    return (
        pathlib.Path(__file__).parent
        / "../../../../../src/tests/resources/broken-project/compute-backend-config.md"  # noqa: E501
    )


@pytest.fixture(scope="session")
def config_with_errors() -> pathlib.Path:
    return (
        pathlib.Path(__file__).parent / "../../../../../src/tests/resources/"
        "test-project/config-with-errors.yaml"
    )


@pytest.fixture(scope="session")
def compute_backend_config_yaml(mlproject_path) -> pathlib.Path:
    """Return the UNICORE config in YAML format.

    Doesn't contain. `Environment` section

    """
    return pathlib.Path(f"{str(mlproject_path)}/compute-backend-config.yaml")


@pytest.fixture(scope="session")
def compute_backend_config_json(mlproject_path) -> pathlib.Path:
    return pathlib.Path(f"{str(mlproject_path)}/compute-backend-config.json")


@pytest.fixture()
def unset_tracking_token_env_var_before_execution():
    if utils.mlflow.TRACKING_TOKEN_ENV_VAR in os.environ:
        del os.environ[utils.mlflow.TRACKING_TOKEN_ENV_VAR]
