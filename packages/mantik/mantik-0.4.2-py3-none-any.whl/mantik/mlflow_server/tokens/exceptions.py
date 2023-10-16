class VerificationFailedException(Exception):
    """Verification of the JWT failed."""


class TokenExpiredException(VerificationFailedException):
    """Token has expired."""


class InvalidSignatureException(VerificationFailedException):
    """Token signature is invalid."""


class InvalidClientException(VerificationFailedException):
    """The client ID in the payload is invalid."""


class InvalidIssuerException(VerificationFailedException):
    """The token issuer is invalid."""


class IncorrectTokenTypeException(VerificationFailedException):
    """The given token type is not correct."""
