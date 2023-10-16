import typing as t


class UnicoreError(Exception):
    """Generic class for all unicore errors."""


class AuthenticationFailedException(UnicoreError):
    """User authentication has failed.

    Unfortunately the response by the server does not give any detailed
    information why the authentication fails.

    """


class ConfigValidationError(Exception):
    """Error raised when validating the config"""


def iterable_to_string(any_list: t.Iterable) -> str:
    return ", ".join(f"{element!r}" for element in any_list)
