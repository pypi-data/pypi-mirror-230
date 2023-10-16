import contextlib

import pytest

import mantik.utils.env as env
import mantik.utils.mantik_api.credentials as _credentials

# Variables have to be renamed for testing. Otherwise, the actual
# variables will be replaced and reset if it is set at the time of the test.
# This does not allow testing cases where the environment variables are not set
# by the user.
_credentials._MANTIK_USERNAME_ENV_VAR = "TEST_MANTIK_USERNAME_ENV_VAR"
_credentials._MANTIK_PASSWORD_ENV_VAR = "TEST_MANTIK_PASSWORD_ENV_VAR"
_credentials._MANTIK_SECRET_ENV_VAR = "TEST_MANTIK_SECRET_ENV_VAR"


class TestCredentials:
    @pytest.mark.parametrize(
        ("env_vars", "expected"),
        [
            (
                {
                    _credentials._MANTIK_USERNAME_ENV_VAR: "test-username",
                    _credentials._MANTIK_PASSWORD_ENV_VAR: "test-password",
                },
                _credentials.Credentials(
                    username="test-username",
                    password="test-password",
                ),
            ),
            # Test case: username env var not set
            (
                {
                    _credentials._MANTIK_USERNAME_ENV_VAR: "test-username",
                },
                NameError(),
            ),
            # Test case: password env var not set
            (
                {
                    _credentials._MANTIK_PASSWORD_ENV_VAR: "test-password",
                },
                NameError(),
            ),
        ],
    )
    def test_from_env(self, env_vars, expected):
        with env.env_vars_set(env_vars):
            with pytest.raises(type(expected)) if isinstance(
                expected, Exception
            ) else contextlib.nullcontext():
                result = _credentials.Credentials.from_env()
                assert result == expected
