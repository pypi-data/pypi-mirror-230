import datetime
import os
import typing as t

import pytest

import mantik.authentication.api as _api
import mantik.authentication.auth as auth
import mantik.authentication.tokens as _tokens
import mantik.testing.env
import mantik.testing.token as testing_token
import mantik.tracking.track as track
import mantik.utils as utils
import mantik.utils.mantik_api.client as mantik_api


@pytest.fixture(autouse=True)
def set_required_env_vars(
    env_vars_set, mantik_api_url, expect_raise_if_exception
):
    env_vars = {mantik_api._MANTIK_API_URL_ENV_VAR: mantik_api_url}
    with env_vars_set(env_vars):
        yield


def test_track_without_existing_tokens(
    requests_mock,
    mantik_api_url,
    tmp_dir_as_test_mantik_folder,
    required_env_vars,
    token_expiration_date,
):
    requests_mock.post(
        url=f"{mantik_api_url}"
        f"{mantik_api.MANTIK_API_CREATE_TOKEN_API_PATH}",
        json={
            "AccessToken": "test-access-token",
            "RefreshToken": "test-refresh-token",
            "ExpiresAt": token_expiration_date.isoformat(),
        },
    )

    _init_tracking_and_assert_expected(
        env_vars=required_env_vars,
        expected_access_token="test-access-token",
    )
    # Cleanup
    os.unsetenv(utils.mlflow.TRACKING_TOKEN_ENV_VAR)


@testing_token.set_token(
    access_token="test-stored-access-token",
    refresh_token="test-stored-refresh-token",
)
def test_track_with_existing_valid_tokens(
    monkeypatch,
    tmp_dir_as_test_mantik_folder,
    required_env_vars,
    token_expiration_date,
):
    _init_tracking_and_assert_expected(
        env_vars=required_env_vars,
        expected_access_token="test-stored-access-token",
    )


@testing_token.set_token(
    access_token="test-stored-expired-access-token",
    refresh_token="test-stored-refresh-token",
    expires_at=datetime.datetime(2020, 1, 1),
)
def test_track_with_existing_expired_token(
    requests_mock,
    mantik_api_url,
    tmp_dir_as_test_mantik_folder,
    required_env_vars,
    token_expiration_date,
):
    requests_mock.post(
        url=f"{mantik_api_url}"
        f"{mantik_api.MANTIK_API_REFRESH_TOKEN_API_PATH}",
        json={
            "AccessToken": "test-refreshed-access-token",
            "ExpiresAt": token_expiration_date.isoformat(),
        },
    )

    _init_tracking_and_assert_expected(
        env_vars=required_env_vars,
        expected_access_token="test-refreshed-access-token",
    )


@testing_token.set_token(
    access_token="test-stored-expired-access-token", refresh_token="test-stored"
)
def test_track_with_existing_expired_token_and_expired_refresh_token(
    requests_mock,
    mantik_api_url,
    tmp_dir_as_test_mantik_folder,
    required_env_vars,
    token_expiration_date,
):
    # Mock refresh api to return expired error
    requests_mock.post(
        url=f"{mantik_api_url}"
        f"{mantik_api.MANTIK_API_REFRESH_TOKEN_API_PATH}",
        status_code=401,
        text=_api.REFRESH_TOKEN_EXPIRED_ERROR_MESSAGE,
    )
    # Mock get api to return refreshed tokens
    requests_mock.post(
        url=(
            f"{mantik_api_url}" f"{mantik_api.MANTIK_API_CREATE_TOKEN_API_PATH}"
        ),
        json={
            "AccessToken": "test-refreshed-access-token",
            "RefreshToken": "test-refreshed-refresh-token",
            "ExpiresAt": token_expiration_date.isoformat(),
        },
    )

    tokens = _tokens.Tokens(
        access_token="test-stored-expired-access-token",
        refresh_token="test-stored-refresh-token",
        expires_at=datetime.datetime(2020, 1, 1),
    )
    tokens.write_to_file(auth._MANTIK_TOKEN_FILE)

    _init_tracking_and_assert_expected(
        env_vars=required_env_vars,
        expected_access_token="test-refreshed-access-token",
    )

    result_tokens = _tokens.Tokens.from_file(auth._MANTIK_TOKEN_FILE)
    assert result_tokens.access_token == "test-refreshed-access-token"
    assert result_tokens.refresh_token == "test-refreshed-refresh-token"
    assert result_tokens.expires_at == token_expiration_date


@testing_token.set_token(
    access_token="test-stored-expired-access-token",
    refresh_token="test-stored-invalid-refresh-token",
    expires_at=datetime.datetime(2020, 1, 1),
)
def test_track_with_existing_invalid_refresh_token(
    requests_mock,
    mantik_api_url,
    tmp_dir_as_test_mantik_folder,
    required_env_vars,
    token_expiration_date,
):
    # Mock refresh api to return invalid error
    requests_mock.post(
        url=f"{mantik_api_url}"
        f"{mantik_api.MANTIK_API_REFRESH_TOKEN_API_PATH}",
        status_code=401,
        text=_api.REFRESH_TOKEN_INVALID_ERROR_MESSAGE,
    )
    # Mock get api to return refreshed tokens
    requests_mock.post(
        url=(
            f"{mantik_api_url}" f"{mantik_api.MANTIK_API_CREATE_TOKEN_API_PATH}"
        ),
        json={
            "AccessToken": "test-refreshed-access-token",
            "RefreshToken": "test-refreshed-refresh-token",
            "ExpiresAt": token_expiration_date.isoformat(),
        },
    )

    _init_tracking_and_assert_expected(
        env_vars=required_env_vars,
        expected_access_token="test-refreshed-access-token",
    )

    result_tokens = _tokens.Tokens.from_file(auth._MANTIK_TOKEN_FILE)
    assert result_tokens.access_token == "test-refreshed-access-token"
    assert result_tokens.refresh_token == "test-refreshed-refresh-token"
    assert result_tokens.expires_at == token_expiration_date


def _init_tracking_and_assert_expected(
    env_vars: t.Dict[str, str],
    expected_access_token: str,
) -> None:
    with utils.env.env_vars_set(env_vars):
        track.init_tracking()

        mantik.testing.env.assert_conflicting_mlflow_env_vars_not_set()
        mantik.testing.env.assert_correct_tracking_token_env_var_set(
            expected_access_token
        )
