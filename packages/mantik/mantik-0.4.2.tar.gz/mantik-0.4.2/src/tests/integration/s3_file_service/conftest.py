import uuid

import pytest

import mantik.utils.mantik_api.connection as connection
import mantik.utils.mantik_api.user as user


@pytest.fixture(scope="session")
def fake_connection_id():
    return uuid.uuid4()


@pytest.fixture(scope="session")
def fake_user_id():
    return uuid.uuid4()


@pytest.fixture()
def mock_get_user_id_from_token(mocker, fake_user_id):
    with mocker.patch(
        "mantik.remote_file_service.s3_file_service._get_sub_from_token",
        return_value=str(fake_user_id),
    ):
        yield


@pytest.fixture()
def mock_login(mocker):
    with mocker.patch(
        "mantik.authentication.auth.get_valid_access_token", return_value="XXX"
    ):
        yield


@pytest.fixture()
def fake_connection(fake_connection_id, fake_user_id):
    return connection.Connection(
        connectionId=fake_connection_id,
        user=user.User(
            userId=uuid.UUID("3fa85f64-5717-4562-b3fc-2c963f66afa6"),
            name="test-name",
            email="email-test",
        ),
        connectionName="s3 connection",
        connectionProvider="ambrosys",
        authMethod="username/password",
        loginName="api-name",
        password="api-password",
    )


@pytest.fixture()
def mock_get_connection(mocker, fake_connection):
    with mocker.patch(
        "mantik.utils.mantik_api.client.get_connection",
        return_value=fake_connection,
    ):
        yield


@pytest.fixture()
def mock_api_creds_retrieval(
    mock_login, mock_get_connection, mock_get_user_id_from_token
):
    yield
