import contextlib
import datetime
import os
import typing as t

import pytest

import mantik.authentication as authentication
import mantik.utils as utils
import mantik.utils.mantik_api.client as mantik_api
import mantik.utils.mantik_api.credentials as _credentials

EXPIRES_AT = datetime.datetime(2022, 1, 1)


@pytest.fixture()
def credentials() -> _credentials.Credentials:
    return _credentials.Credentials(
        username="test-user",
        password="test-password",
    )


def test_create_tokens(requests_mock, credentials):
    requests_mock.post(
        url=f"{mantik_api._DEFAULT_MANTIK_API_URL}"
        f"{mantik_api.MANTIK_API_CREATE_TOKEN_API_PATH}",
        json={
            "AccessToken": "test-access-token",
            "RefreshToken": "test-refresh-token",
            "ExpiresAt": EXPIRES_AT.isoformat(),
        },
    )

    result = authentication.api.create_tokens(credentials=credentials)

    assert result == authentication.tokens.Tokens(
        access_token="test-access-token",
        refresh_token="test-refresh-token",
        expires_at=EXPIRES_AT,
    )


def test_refresh_tokens(
    requests_mock,
    credentials,
):
    requests_mock.post(
        url=f"{mantik_api._DEFAULT_MANTIK_API_URL}"
        f"{mantik_api.MANTIK_API_REFRESH_TOKEN_API_PATH}",
        json={
            "AccessToken": "test-refreshed-access-token",
            "RefreshToken": "test-refreshed-refresh-token",
            "ExpiresAt": EXPIRES_AT.isoformat(),
        },
    )

    tokens = authentication.tokens.Tokens(
        access_token="test-access-token",
        refresh_token="test-refresh-token",
        expires_at=datetime.datetime(2000, 1, 1),
    )

    result = authentication.api.refresh_tokens(
        credentials=credentials,
        tokens=tokens,
    )

    assert result == authentication.tokens.Tokens(
        access_token="test-refreshed-access-token",
        refresh_token="test-refresh-token",
        expires_at=EXPIRES_AT,
    )


@contextlib.contextmanager
def _set_mlflow_tracking_uri_env_var(value: t.Optional[str]) -> None:
    if os.environ.get(utils.mlflow.TRACKING_URI_ENV_VAR):
        os.environ.pop(utils.mlflow.TRACKING_URI_ENV_VAR)
    if value is not None:
        os.environ[utils.mlflow.TRACKING_URI_ENV_VAR] = value
    yield
    if os.environ.get(utils.mlflow.TRACKING_URI_ENV_VAR):
        os.environ.pop(utils.mlflow.TRACKING_URI_ENV_VAR)
