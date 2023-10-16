"""JWT validation.

See
https://docs.aws.amazon.com/cognito/latest/developerguide/amazon-cognito-user-pools-using-tokens-verifying-a-jwt.html  # noqa

"""
import logging
import typing as t

import mantik.mlflow_server.tokens.cognito as _cognito
import mantik.mlflow_server.tokens.exceptions as exceptions
import mantik.mlflow_server.tokens.jwks as _jwks
import mantik.mlflow_server.tokens.jwt as _jwt

logger = logging.getLogger(__name__)


class TokenVerifier:
    """Verify JWTs."""

    def __init__(
        self,
        cognito: t.Optional[_cognito.client.Properties] = None,
        jwks: t.Optional[_jwks.JWKS] = None,
        secret_required: t.Optional[bool] = None,
    ):
        """Get JWKS file if not given."""
        if cognito is None:
            self._ensure_secret_required_parameter_is_set(secret_required)
            cognito = _cognito.client.Properties.from_env(
                secret_required=secret_required
            )

        self.cognito = cognito
        self.jwks = jwks or _jwks.JWKS.from_cognito(self.cognito)

    @staticmethod
    def _ensure_secret_required_parameter_is_set(
        secret_required: t.Optional[bool] = None,
    ) -> None:
        """Ensure that the secret parameter is set and not `None`.

        The class allows an optional injection of the Cognito Properties. If
        these are not injected, they are initialized in this class. This,
        however, requires to pass a flag `secret_required` that - if `True` -
        triggers that the environment variable for the Cognito App Client
        secret is read.

        Hence, it must be ensured that this flag is given if the Cognito
        Properties are not injected.

        """
        if secret_required is None:
            raise RuntimeError(
                "If Cognito Properties are not injected, it has to be "
                "defined whether the Cognito App Client secret is required"
            )

    def verify_token(self, token: str) -> None:
        """Return whether a given token is valid.

        Parameters
        ----------
        token : str
            The token to verify.

        Raises
        ------
        ValidationFailedException
            The given token is not valid.

        """
        logger.debug("Verifying token %s", token)
        jwt = _jwt.JWT.from_token(token)
        self._verify_token_signature_and_claims(jwt)

    def _verify_token_signature_and_claims(self, jwt: _jwt.JWT) -> None:
        _verify_signature(jwt, jwks=self.jwks)
        _verify_expiration(jwt)
        _verify_client(jwt, cognito=self.cognito)
        _verify_issuer(jwt, cognito=self.cognito)
        _verify_token_type(jwt)


def _verify_signature(
    jwt: _jwt.JWT,
    jwks: _jwks.JWKS,
) -> None:
    if not jwks.signature_valid(jwt):
        raise exceptions.InvalidSignatureException("Invalid signature")


def _verify_expiration(jwt: _jwt.JWT) -> None:
    if jwt.has_expired:
        raise exceptions.TokenExpiredException("Token expired")


def _verify_client(jwt: _jwt.JWT, cognito: _cognito.client.Properties) -> None:
    if not jwt.issued_by_client(cognito):
        raise exceptions.InvalidClientException(
            "Token issued by unauthorized client"
        )


def _verify_issuer(jwt: _jwt.JWT, cognito: _cognito.client.Properties) -> None:
    if not jwt.issued_by_user_pool(cognito):
        raise exceptions.InvalidIssuerException(
            "Token issued by unauthorized client"
        )


def _verify_token_type(jwt: _jwt.JWT) -> None:
    if not jwt.is_access_token():
        raise exceptions.IncorrectTokenTypeException(
            f"Token type '{jwt.token_type}' not allowed ('access' required)"
        )
