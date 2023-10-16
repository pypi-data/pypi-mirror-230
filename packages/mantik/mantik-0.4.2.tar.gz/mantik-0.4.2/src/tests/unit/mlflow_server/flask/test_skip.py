import pytest

import mantik.mlflow_server.flask.skip as skip


def func_without_skip_flag() -> None:
    pass


@skip.skip_authentication
def func_with_skip_flag() -> None:
    pass


@pytest.mark.parametrize(
    ("func", "expected"),
    [
        (func_without_skip_flag, False),
        (func_with_skip_flag, True),
    ],
)
def test_has_skip_authentication_flag(func, expected):
    result = skip.has_skip_authentication_flag(func)

    assert result == expected
