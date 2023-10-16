import contextlib
import datetime
import logging
import os
import pathlib
import typing as t

import pytest
import requests_mock

import mantik.authentication.auth as track
import mantik.unicore.config.environment
import mantik.utils as utils
import mantik.utils.mantik_api.client as mantik_api
import mantik.utils.mantik_api.credentials as _credentials
import mantik.utils.mantik_api.data_repository as data_repository


@pytest.fixture()
def mantik_api_url() -> str:
    return "https://api.test.com"


@pytest.fixture()
def mlflow_tracking_uri() -> str:
    return "https://tracking.test-uri.com"


@pytest.fixture()
def required_env_vars(mlflow_tracking_uri) -> t.Dict[str, str]:
    return {
        _credentials._MANTIK_USERNAME_ENV_VAR: "test-user",
        _credentials._MANTIK_PASSWORD_ENV_VAR: "test-password",
        utils.mlflow.TRACKING_URI_ENV_VAR: mlflow_tracking_uri,
        # If the env vars for MLflow user/password are set, these are
        # prioritized by MLflow over the token. This leads to an
        # `Unauthorized` error.
        utils.mlflow.TRACKING_USERNAME_ENV_VAR: "must-be-unset",
        utils.mlflow.TRACKING_PASSWORD_ENV_VAR: "must-be-unset",
    }


@pytest.fixture()
def token_expiration_date() -> datetime.datetime:
    return datetime.datetime(2022, 1, 1)


@pytest.fixture()
def tmp_dir_as_test_mantik_folder(tmp_path):
    track._MANTIK_FOLDER = pathlib.Path(tmp_path)
    track._MANTIK_TOKEN_FILE = track._MANTIK_FOLDER / "tokens.json"
    return tmp_path


def pytest_configure(config):
    """Remove all MLFLOW_ related environment variables before running any
    test to simplify tests setup."""
    for env in mantik.unicore.config.environment._get_mlflow_env_vars():
        del os.environ[env]


@pytest.fixture
def mock_mantik_api_request(
    env_vars_set, mantik_api_url, expect_raise_if_exception
):
    @contextlib.contextmanager
    def wrapped(
        method: str,
        end_point: str,
        status_code: int,
        json_response: dict,
        expected_error: t.Optional[Exception] = None,
    ) -> None:
        env_vars = {mantik_api._MANTIK_API_URL_ENV_VAR: mantik_api_url}
        with requests_mock.Mocker() as m, env_vars_set(
            env_vars
        ), expect_raise_if_exception(expected_error) as e:
            m.register_uri(
                method=method,
                url=f"{mantik_api_url}{end_point}",
                status_code=status_code,
                json=json_response,
            )
            yield m, e

    return wrapped


@pytest.fixture()
def user_id():
    return "7fc6a4c0-0eb2-4ca0-9e18-c517d7dc92a5"


@pytest.fixture()
def mock_token_sub(mocker, user_id):
    with mocker.patch(
        "mantik.unicore.credentials._get_sub_from_token", return_value=user_id
    ) as mock_sub:
        yield mock_sub


@pytest.fixture
def add_data_repository():
    return data_repository.AddDataRepositoryModel(
        uri="test_uri",
        data_repository_name="test_name",
        access_token=None,
        description="test_description",
    )


@pytest.fixture
def info_caplog(caplog):
    caplog.set_level(logging.INFO)
    yield caplog
