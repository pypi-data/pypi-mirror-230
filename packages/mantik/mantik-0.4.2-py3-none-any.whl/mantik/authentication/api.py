import logging
import typing as t

import requests

import mantik.authentication.tokens as _tokens
import mantik.utils.mantik_api.client as mantik_api
import mantik.utils.mantik_api.credentials as _credentials

logger = logging.getLogger(__name__)

REFRESH_TOKEN_EXPIRED_ERROR_MESSAGE = "Refresh token has expired"
REFRESH_TOKEN_INVALID_ERROR_MESSAGE = "Refresh token is invalid"


def create_tokens(
    credentials: t.Optional[_credentials.Credentials] = None,
) -> _tokens.Tokens:
    logger.info("Creating new tokens")
    return _tokens.Tokens.from_json_response(
        mantik_api.create_tokens(credentials)
    )


def refresh_tokens(
    tokens: _tokens.Tokens,
    credentials: t.Optional[_credentials.Credentials] = None,
) -> _tokens.Tokens:
    """Refresh the tokens.

    Raises
    ------
    RuntimeError
        If MLflow tracking URI environment variable is not set.

    Notes
    -----
    Refreshing a password requires to send the refresh token instead of the
    user's password.

    """
    logger.debug("Refreshing access token")
    try:
        return _tokens.Tokens.from_json_response(
            mantik_api.refresh_tokens(
                refresh_token=tokens.refresh_token,
                access_credentials=credentials,
            ),
            refresh_token=tokens.refresh_token,
        )
    except requests.HTTPError as e:
        if _refresh_token_has_expired(e) or _refresh_token_is_invalid(e):
            logger.debug("Refresh token has expired or is invalid")
            return create_tokens(credentials)
        raise e


def _refresh_token_has_expired(e: requests.HTTPError) -> bool:
    return (
        e.response.status_code == 401
        and REFRESH_TOKEN_EXPIRED_ERROR_MESSAGE in e.response.text
    )


def _refresh_token_is_invalid(e: requests.HTTPError) -> bool:
    return (
        e.response.status_code == 401
        and REFRESH_TOKEN_INVALID_ERROR_MESSAGE in e.response.text
    )
