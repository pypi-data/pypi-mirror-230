import datetime
import pathlib

import freezegun
import pytest

import mantik.authentication.tokens as _tokens


@pytest.fixture()
def tokens():
    return _tokens.Tokens(
        access_token="test-access-token",
        refresh_token="test-refresh-token",
        expires_at=datetime.datetime(
            2000, 1, 1, 1, 30, tzinfo=datetime.timezone.utc
        ),
    )


class TestTokens:
    @pytest.mark.parametrize(
        ("current_date", "expected"),
        [
            ("2000-01-01T01:00", False),
            ("2000-01-01T02:00", True),
        ],
    )
    def test_has_expired(self, tokens, current_date, expected):
        with freezegun.freeze_time(current_date):
            result = tokens.has_expired

            assert result == expected

    @pytest.mark.parametrize(
        "path",
        ["test-tokens.json", "subfolder/test-tokens.json"],
    )
    def test_write_to_and_from_file(self, tmpdir, tokens, path):
        file = tmpdir / path
        as_path = pathlib.Path(file)
        tokens.write_to_file(as_path)

        result = tokens.from_file(as_path)

        assert result == tokens
