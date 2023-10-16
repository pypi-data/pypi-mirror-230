import pytest

import mantik.unicore.credentials as credentials


@pytest.fixture()
def token():
    return (
        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
        "eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6I"
        "kpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ."
        "SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
    )


@pytest.fixture()
def sub():
    return "1234567890"


def test_get_sub_from_token(token, sub):
    assert credentials._get_sub_from_token(token) == sub
