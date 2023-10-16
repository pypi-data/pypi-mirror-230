"""JWT validation.

Inspired by https://github.com/jgontrum/fastapi_jwt_auth_with_aws_cognito

"""
import logging
import typing as t

import jose.backends
import jose.jwk
import pydantic
import requests

import mantik.mlflow_server.tokens.cognito as _cognito
import mantik.mlflow_server.tokens.exceptions as exceptions
import mantik.mlflow_server.tokens.jwt as _jwt

logger = logging.getLogger(__name__)

JWK = t.Dict[str, str]


class JWKS(pydantic.BaseModel):
    """Represents the content of the jwks.json file of the User Pool."""

    keys: t.List[JWK]
    kid_to_jwk_mapping: t.Dict[str, JWK] = None

    @pydantic.validator("kid_to_jwk_mapping", always=True)
    def _construct_kid_to_jwk_mapping(cls, v, values) -> t.Dict[str, JWK]:
        """Create the object at initialization."""
        return {jwk["kid"]: jwk for jwk in values["keys"]}

    @classmethod
    def from_cognito(cls, cognito: _cognito.client.Properties) -> "JWKS":
        """Construct from AWS Cognito user pool."""
        jwks_file = requests.get(cognito.jwks_file_url).json()
        return cls.parse_obj(jwks_file)

    def signature_valid(self, jwt: _jwt.JWT) -> bool:
        """Return whether the signature of the given token is valid.

        Parameters
        ----------
        jwt : JWT
            The JWT whose signature to validate.

        Raises
        ------
        VerificationFailedException
            The key ID of the public key in the JWT's signature could not
            be found in the jwks.json file.

        """
        key = self._get_public_key(kid=jwt.kid)
        return key.verify(
            msg=jwt.encoded_message,
            sig=jwt.encoded_signature,
        )

    def _get_public_key(self, kid: str) -> jose.backends.base.Key:
        try:
            public_key = self.kid_to_jwk_mapping[kid]
        except KeyError:
            logger.exception(
                "Could not find public key %s in %s",
                kid,
                self.kid_to_jwk_mapping,
            )
            raise exceptions.VerificationFailedException("Invalid token")
        return jose.jwk.construct(public_key)
