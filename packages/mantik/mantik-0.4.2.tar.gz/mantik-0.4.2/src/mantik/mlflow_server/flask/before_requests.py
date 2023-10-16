import logging
import os

import flask

import mantik.mlflow_server.flask._header as _header
import mantik.mlflow_server.flask.app as _app
import mantik.mlflow_server.flask.skip as skip
import mantik.mlflow_server.tokens as tokens

app = _app.app

logger = logging.getLogger(__name__)

_API_PATH_PREFIX = os.environ.get("API_PATH_PREFIX", "/api")


class AuthenticationFailedException(Exception):
    """Authentication has failed."""


@app.before_request
def authenticate_api_calls():
    """Authenticate all calls to the API path.

    Notes
    -----
    Returning `None` forwards the request as usual.

    """
    if _skip_authentication(flask.request):
        return

    try:
        _verify_token(flask.request)
    except AuthenticationFailedException as e:
        logger.debug(
            "Token in request headers %s is not valid",
            flask.request.headers,
            exc_info=True,
        )
        return flask.make_response(str(e), 401)
    return


def _skip_authentication(request: flask.Request) -> bool:
    if os.getenv("TESTING_SKIP_TOKEN_VERIFICATION", "False").lower() == "true":
        logger.warning("SKIPPING TOKEN VERIFICATION")
        return True

    if not _request_to_api_path(request):
        return True

    if request.endpoint in app.view_functions:
        func = app.view_functions[request.endpoint]
        return skip.has_skip_authentication_flag(func)
    return False


def _request_to_api_path(request: flask.Request) -> bool:
    return request.path.startswith(_API_PATH_PREFIX)


def _verify_token(request: flask.Request) -> None:
    verifier = tokens.verifier.TokenVerifier(secret_required=True)
    try:
        token = _header.get_authorization_token(request)
        verifier.verify_token(token)
    except (
        _header.MissingAuthorizationHeaderException,
        _header.EmptyTokenException,
        tokens.exceptions.VerificationFailedException,
    ) as e:
        raise AuthenticationFailedException(str(e))
