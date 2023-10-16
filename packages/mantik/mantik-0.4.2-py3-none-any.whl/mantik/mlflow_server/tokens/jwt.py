"""JWT validation.

Inspired by https://github.com/jgontrum/fastapi_jwt_auth_with_aws_cognito

"""
import datetime
import logging
import typing as t

import jose.jwt
import jose.utils
import pydantic

import mantik.mlflow_server.tokens.cognito as _cognito
import mantik.mlflow_server.tokens.exceptions as exceptions

logger = logging.getLogger(__name__)


class JWT(pydantic.BaseModel):
    """Holds the content of a JWT."""

    jwt_token: str
    header: t.Dict[str, str]
    claims: t.Dict[str, str]
    signature: str
    message: str

    @classmethod
    def from_token(cls, token: str) -> "JWT":
        """Create from a given token.

        Parameters
        ----------
        token : str
            The token to read.

        Raises
        ------
        VerificationFailedException
            Reading of the token has failed.

        """
        message, signature = _separate_message_and_signature(token)
        try:
            return cls(
                jwt_token=token,
                header=jose.jwt.get_unverified_headers(token),
                claims=jose.jwt.get_unverified_claims(token),
                signature=signature,
                message=message,
            )
        except jose.JWTError:
            logger.error(
                "Failed to construct credentials from JWT", exc_info=True
            )
            raise exceptions.VerificationFailedException("Invalid token")

    @property
    def kid(self) -> str:
        """Return the kid."""
        return self.header["kid"]

    @property
    def encoded_message(self) -> bytes:
        """Return the encoded message."""
        return self.message.encode("utf-8")

    @property
    def encoded_signature(self) -> bytes:
        """Return the encoded signature."""
        return jose.utils.base64url_decode(self.signature.encode("utf-8"))

    @property
    def has_expired(self) -> bool:
        """Return whether the token has expired."""
        return datetime.datetime.now() > self.expires_at

    @property
    def token_type(self) -> str:
        """Return the token type."""
        return self.claims["token_use"]

    @property
    def expires_at(self) -> datetime.datetime:
        """Return the expiration date."""
        return datetime.datetime.fromtimestamp(int(self.claims["exp"]))

    def issued_by_client(self, cognito: _cognito.client.Properties) -> bool:
        """Return whether token was issued by client with given ID."""
        return self.claims["client_id"] == cognito.app_client_id

    def issued_by_user_pool(self, cognito: _cognito.client.Properties) -> bool:
        """Return whether token was issued by given user pool."""
        return self.claims["iss"] == cognito.idp_url

    def is_access_token(self) -> bool:
        """Return whether the given token as an access token."""
        return self.token_type == "access"


def _separate_message_and_signature(token: str) -> t.Tuple[str, str]:
    try:
        message, signature = token.rsplit(".", 1)
    except ValueError:
        logger.exception(
            "Splitting of JWT into message and signature failed",
            exc_info=True,
        )
        raise exceptions.VerificationFailedException("Invalid token")
    return message, signature
