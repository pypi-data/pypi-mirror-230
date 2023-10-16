import os

import pytest

import mantik.utils.env as env


@pytest.mark.parametrize(
    ("name", "expected"),
    [
        ("TEST", "test"),
        ("TEST_NOT_SET", NameError()),
    ],
)
def test_get_required_env_var(expect_raise_if_exception, name, expected):
    if not isinstance(expected, Exception):
        os.environ[name] = "test"

    with expect_raise_if_exception(expected):
        result = env.get_required_env_var(name)
        os.unsetenv(name)

        assert result == expected


def test_set_env_vars():
    name = "TEST_ENV_VAR"
    value = "test-value"
    env_vars = {
        name: value,
    }

    env.set_env_vars(env_vars)

    assert os.getenv(name) == value

    os.unsetenv(name)
