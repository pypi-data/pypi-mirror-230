import pytest

import mantik.unicore.config._utils as _utils
import mantik.unicore.exceptions as exceptions


@pytest.mark.parametrize(
    ("name", "value_type", "config", "expected"),
    [
        ("given", str, {"given": "value"}, "value"),
        (
            "given_with_incorrect_type",
            int,
            {"given_with_incorrect_type": "value"},
            exceptions.ConfigValidationError(),
        ),
        (
            "not_given",
            str,
            {"given": "value"},
            exceptions.ConfigValidationError(),
        ),
    ],
)
def test_get_required_config_value(
    expect_raise_if_exception, name, value_type, config, expected
):
    with expect_raise_if_exception(expected):
        result = _utils.get_required_config_value(
            name=name,
            value_type=value_type,
            config=config,
        )

        assert result == expected


@pytest.mark.parametrize(
    ("name", "value_type", "default", "config", "expected"),
    [
        ("given", str, None, {"given": "value"}, "value"),
        (
            "given_with_incorrect_type",
            int,
            None,
            {"given_with_incorrect_type": "value"},
            exceptions.ConfigValidationError(),
        ),
        ("not_given", str, None, {"given": "value"}, None),
        ("not_given", str, None, {"given": "value"}, None),
        ("not_given", str, "default", {"given": "value"}, "default"),
    ],
)
def test_get_optional_config_value(
    expect_raise_if_exception,
    name,
    value_type,
    default,
    config,
    expected,
    caplog,
):
    with expect_raise_if_exception(expected):
        _utils.logger.setLevel("DEBUG")
        result = _utils.get_optional_config_value(
            name=name,
            value_type=value_type,
            config=config,
            default=default,
        )

        assert result == expected
        if expected is None:
            assert "DEBUG" in caplog.text
