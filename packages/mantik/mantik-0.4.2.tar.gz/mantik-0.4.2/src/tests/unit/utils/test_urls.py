import pytest

import mantik.utils.urls as urls


@pytest.mark.parametrize(
    ("url", "expected"),
    [
        (
            "http://test-url.com/path//with/double//slashes",
            "https://test-url.com/path/with/double/slashes",
        ),
        # Test case: also works with 3 slashes
        (
            "http://test-url.com///path//with/double//slashes",
            "https://test-url.com/path/with/double/slashes",
        ),
    ],
)
def test_ensure_https_and_remove_double_slashes_from_path(url, expected):
    result = urls.ensure_https_and_remove_double_slashes_from_path(url)

    assert result == expected


@pytest.mark.parametrize(
    ("url", "expected"),
    [
        (
            "http://test.domain.de",
            "https://replaced.domain.de",
        ),
        (
            "https://test.domain.de",
            "https://replaced.domain.de",
        ),
        (
            "http://www.test.domain.de",
            "https://www.replaced.domain.de",
        ),
        (
            "https://www.test.domain.de",
            "https://www.replaced.domain.de",
        ),
        (
            "https://www.test.another.domain.de",
            "https://www.replaced.another.domain.de",
        ),
    ],
)
def test_replace_first_subdomain(url, expected):
    result = urls.replace_first_subdomain(url, replace_with="replaced")

    assert result == expected
