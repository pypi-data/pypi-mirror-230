import datetime
import uuid

import pytest

import mantik.remote_file_service.data_client as _data_client
import mantik.testing.remote_file_service as remote_file_service
import mantik.utils.mantik_api.client as mantik_api
import mantik.utils.mantik_api.credentials as _credentials


@pytest.fixture
def project_id():
    return uuid.UUID("3aeb9774-040e-477e-ae90-878a41c11f80")


@pytest.fixture
def envs():
    _credentials._MANTIK_USERNAME_ENV_VAR = "TEST_MANTIK_USERNAME_ENV_VAR"
    _credentials._MANTIK_PASSWORD_ENV_VAR = "TEST_MANTIK_PASSWORD_ENV_VAR"
    return {
        "TEST_MANTIK_USERNAME_ENV_VAR": "username",
        "TEST_MANTIK_PASSWORD_ENV_VAR": "password",
        "MANTIK_API_USER_ID": "1f981daf-1a2c-4759-a6f1-d25bf8d1d9e7",
    }


@pytest.fixture
def data_client(
    env_vars_set, envs, requests_mock, mocker, project_id
) -> _data_client.DataClient:
    mocker.patch("pathlib.Path.exists", return_value=False)
    requests_mock.post(
        url=f"{mantik_api._DEFAULT_MANTIK_API_URL}"
        f"{mantik_api.MANTIK_API_CREATE_TOKEN_API_PATH}",
        json={
            "AccessToken": "test-access-token",
            "RefreshToken": "test-refresh-token",
            "ExpiresAt": datetime.datetime(2022, 1, 1).isoformat(),
        },
    )

    with env_vars_set(envs):
        yield _data_client.DataClient(
            project_id=project_id,
            file_service=remote_file_service.FakeUnicoreFileService(),
        )


@pytest.fixture
def fake_unicore_fs() -> remote_file_service.FakeUnicoreFileService:
    return remote_file_service.FakeUnicoreFileService()
