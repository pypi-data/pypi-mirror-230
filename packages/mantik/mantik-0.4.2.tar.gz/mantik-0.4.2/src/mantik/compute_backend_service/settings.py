import functools

import pydantic

DEFAULT_MAX_SIZE = 104857600


class Settings(pydantic.BaseSettings):
    """App settings.

    Attributes
    ----------
    max_file_size : int, default=104857600
        Maximum file size in bytes that is accepted by the API.
    Defaults to 100MB.
    """

    max_file_size: int = DEFAULT_MAX_SIZE


@functools.lru_cache()
def get_settings() -> Settings:
    """Get settings, to be used as fastapi Dependency.

    Notes
    -----
    :py:class:`pydantic.BaseSettings` automatically reads environment
    variables or `.env` files.
    If :py:class:`~Settings` were directly upon each dependency, env vars
    would be read at runtime, not at startup (which may or may not be
    beneficial). :py:meth:`functools.lru_cache` is used here to effectively
    create a singleton object for the settings that is only read once upon
    first usage.

    Since using pydantic is idiomatic for FastAPI and the
    :py:meth:`functools.lru_cache` provides some extra security and clarity
    about reading of env vars, this seems to be the idiomatic FastAPI way to
    handle settings injection.

    Returns
    -------
    Settings

    """
    return Settings()
