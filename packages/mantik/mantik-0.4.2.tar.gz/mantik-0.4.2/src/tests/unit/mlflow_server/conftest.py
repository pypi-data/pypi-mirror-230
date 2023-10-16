import json
import pathlib
import typing as t

import pytest

_FILE_PATH = pathlib.Path(__file__).parent


@pytest.fixture()
def cognito_auth_response() -> t.Dict:
    path = _FILE_PATH / "../../resources/cognito/auth-response.json"
    return _open_json_file(path)


@pytest.fixture()
def cognito_refresh_response() -> t.Dict:
    path = _FILE_PATH / "../../resources/cognito/refresh-response.json"
    return _open_json_file(path)


@pytest.fixture()
def cognito_incorrect_login_credentials_response() -> t.Dict:
    path = _FILE_PATH / (
        "../../resources/cognito/" "incorrect-login-credentials-response.json"
    )
    return _open_json_file(path)


@pytest.fixture()
def cognito_user_not_found_response() -> t.Dict:
    path = _FILE_PATH / "../../resources/cognito/user-not-found-response.json"
    return _open_json_file(path)


@pytest.fixture()
def cognito_refresh_token_expired_response() -> t.Dict:
    path = (
        _FILE_PATH
        / "../../resources/cognito/refresh-token-expired-response.json"
    )
    return _open_json_file(path)


@pytest.fixture()
def cognito_refresh_token_invalid_response() -> t.Dict:
    path = (
        _FILE_PATH
        / "../../resources/cognito/refresh-token-invalid-response.json"
    )
    return _open_json_file(path)


@pytest.fixture()
def cognito_different_client_response() -> t.Dict:
    path = _FILE_PATH / "../../resources/cognito/different-client.json"
    return _open_json_file(path)


def _open_json_file(path: pathlib.Path) -> t.Dict:
    with open(path) as json_response:
        return json.load(json_response)
