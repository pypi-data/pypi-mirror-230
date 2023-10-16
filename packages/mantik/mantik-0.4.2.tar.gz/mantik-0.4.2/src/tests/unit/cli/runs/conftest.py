import unittest.mock

import pytest

import mantik.testing.pyunicore as testing
import mantik.unicore.config.core as core
import mantik.unicore.credentials as unicore_credentials


@pytest.fixture
def fake_client():
    with unittest.mock.patch(
        "mantik.unicore._connect.create_unicore_api_connection",
        return_value=testing.FakeClient(),
    ) as mock:
        yield mock


@pytest.fixture
def mantik_env_variables():
    return {
        unicore_credentials._USERNAME_ENV_VAR: "test-user",
        unicore_credentials._PASSWORD_ENV_VAR: "test-password",
        core._PROJECT_ENV_VAR: "test-project",
    }
