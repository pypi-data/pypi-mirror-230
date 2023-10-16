import logging
import pathlib

import mantik.authentication.api as api
import mantik.authentication.tokens as _tokens

logger = logging.getLogger(__name__)

_MANTIK_FOLDER = pathlib.Path.home() / ".mantik"
_MANTIK_TOKEN_FILE = _MANTIK_FOLDER / "tokens.json"


def get_valid_access_token() -> str:
    """Authenticate at Mantik.

    Returns
    -------
    Access Token: str

    Notes
    -----
    Mantik prioritizes the username and password environment variables over
    the token variable, causing an `Unauthorized` error. As a consequence,
    these have to be unset before setting the token variable.

    The tokens will be stored in a file `~/.mantik/tokens.json` to reuse
    tokens and refresh them only if they have expired.

    """
    logger.debug("Getting tokens")
    tokens = _get_and_store_tokens()
    return tokens.access_token


def _get_and_store_tokens() -> _tokens.Tokens:
    if not _MANTIK_TOKEN_FILE.exists():
        logger.debug(
            "No existing tokens file found at %s", _MANTIK_TOKEN_FILE.as_posix()
        )
        return _create_and_store_new_tokens()
    return _read_stored_tokens()


def _create_and_store_new_tokens() -> _tokens.Tokens:
    logger.debug(
        "Creating new tokens to store to %s", _MANTIK_TOKEN_FILE.as_posix()
    )
    tokens = api.create_tokens()
    tokens.write_to_file(_MANTIK_TOKEN_FILE)
    return tokens


def _read_stored_tokens() -> _tokens.Tokens:
    logger.debug(
        "Reading stored tokens from file %s", _MANTIK_TOKEN_FILE.as_posix()
    )
    tokens = _tokens.Tokens.from_file(_MANTIK_TOKEN_FILE)
    if tokens.has_expired:
        logger.debug("Access token has expired")
        refreshed = api.refresh_tokens(tokens=tokens)
        refreshed.write_to_file(_MANTIK_TOKEN_FILE)
        return refreshed
    return tokens
