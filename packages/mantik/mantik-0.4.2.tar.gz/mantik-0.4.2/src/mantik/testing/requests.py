import dataclasses
import typing as t

import requests


def fake_get(
    monkeypatch,
    response_urls: t.Sequence[str],
    status_code: int = 200,
    expect_in_request_url: t.Optional[str] = None,
) -> None:
    """Fake `requests.get`."""
    urls_iter = iter(response_urls)

    def fake_response(url: str, *args, **kwargs):
        if (
            expect_in_request_url is not None
            and expect_in_request_url not in url
        ):
            raise ValueError(
                f"Expected '{expect_in_request_url}' to be present in the "
                f"request URL {url}"
            )

        return FakeResponse(url=next(urls_iter), status_code=status_code)

    monkeypatch.setattr(requests, "get", fake_response)


@dataclasses.dataclass
class FakeResponse(requests.Response):
    """Represents a response from the `requests` library."""

    url: str
    status_code: int
    reason = "test-reason"
