import typing as t

import fastapi
import fastapi.security as security
import starlette.requests as requests
import starlette.status as status

import mantik.mlflow_server.tokens as _tokens


class UnauthorizedException(fastapi.HTTPException):
    """Authentication has failed."""

    def __init__(
        self,
        detail: str,
    ) -> None:
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers=None,
        )


class JWTBearer(security.HTTPBearer):
    """Reads the bearer token from the header and verifies it."""

    async def __call__(self, request: requests.Request) -> None:
        """Verify the bearer token in the request header."""
        token = await self._get_token_from_request_header(request)
        _verify_token(token)

    async def _get_token_from_request_header(
        self, request: requests.Request
    ) -> str:
        try:
            credentials: t.Optional[
                security.HTTPAuthorizationCredentials
            ] = await super().__call__(request)
        except fastapi.HTTPException:
            raise UnauthorizedException(
                "Request missing 'Authorization' header "
                "or incorrect scheme used ('Bearer' required)"
            )

        if credentials is None:
            raise UnauthorizedException(
                "Token missing in 'Authorization' header"
            )

        return credentials.credentials


def _verify_token(token: str) -> None:
    verifier = _tokens.verifier.TokenVerifier(secret_required=False)
    try:
        verifier.verify_token(token)
    except _tokens.exceptions.VerificationFailedException as e:
        raise UnauthorizedException(str(e))
