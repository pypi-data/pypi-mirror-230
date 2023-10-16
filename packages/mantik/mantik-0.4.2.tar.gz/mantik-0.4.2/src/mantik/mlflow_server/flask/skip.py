import functools
import typing as t

Endpoint = t.Callable

_SKIP_AUTHENTICATION_ATTRIBUTE_NAME = "_skip_authentication"


def skip_authentication(func: Endpoint) -> Endpoint:
    """Set an attribute flag to a method to skip authentication."""
    setattr(func, _SKIP_AUTHENTICATION_ATTRIBUTE_NAME, True)

    @functools.wraps(func)
    def wrapped(*endpoint_args, **endpoint_kw) -> t.Any:
        return func(*endpoint_args, **endpoint_kw)

    return wrapped


def has_skip_authentication_flag(func: Endpoint) -> bool:
    """Return whether the given endpoint method has the skip flag."""
    return hasattr(func, _SKIP_AUTHENTICATION_ATTRIBUTE_NAME) and getattr(
        func, _SKIP_AUTHENTICATION_ATTRIBUTE_NAME
    )
