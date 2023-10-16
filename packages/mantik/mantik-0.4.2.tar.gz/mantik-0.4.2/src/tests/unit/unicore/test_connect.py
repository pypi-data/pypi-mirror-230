import functools

import pytest
import pyunicore.client as pyunicore

import mantik.testing as testing
import mantik.unicore._connect as _connect
import mantik.unicore.exceptions


@pytest.fixture()
def transport():
    return testing.pyunicore.FakeTransport()


def create_fake_client(login_successful: bool) -> functools.partial:
    return functools.partial(
        testing.pyunicore.FakeClient,
        login_successful=login_successful,
    )


@pytest.mark.parametrize(
    ("login_successful", "expected"),
    [
        (False, mantik.unicore.exceptions.AuthenticationFailedException()),
        (True, testing.pyunicore.FakeClient),
    ],
)
def test_create_unicore_api_connection(
    expect_raise_if_exception, monkeypatch, login_successful, expected
):
    monkeypatch.setattr(pyunicore, "Transport", testing.pyunicore.FakeTransport)
    monkeypatch.setattr(
        pyunicore,
        "Client",
        create_fake_client(login_successful=login_successful),
    )

    api_url = "test-api-url"
    user = "test_user"
    password = "test_password"

    with expect_raise_if_exception(expected):
        result = _connect.create_unicore_api_connection(
            api_url=api_url,
            user=user,
            password=password,
        )

        assert isinstance(result, expected)


def test_create_token():
    user = "test_user"
    password = "test_password"
    expected = "dGVzdF91c2VyOnRlc3RfcGFzc3dvcmQ="

    result = _connect._create_token(user=user, password=password)

    assert result == expected


@pytest.mark.parametrize(
    ("login", "expected"),
    [
        ({}, True),
        ({"test_login_info": "test_login"}, False),
    ],
)
def test_authentication_failed(login, expected):
    client = testing.pyunicore.FakeClient()
    client.add_login_info(login)

    result = _connect._authentication_failed(client)

    assert result == expected
