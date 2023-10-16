import freezegun
import pytest

import mantik.mlflow_server.tokens.cognito as _cognito
import mantik.mlflow_server.tokens.exceptions as exceptions
import mantik.mlflow_server.tokens.verifier as _verifier
import mantik.testing as testing


@pytest.fixture()
def verifier() -> _verifier.TokenVerifier:
    cognito = _cognito.client.Properties(
        region=testing.mlflow_server.FAKE_COGNITO_REGION,
        user_pool_id=testing.mlflow_server.FAKE_COGNITO_USER_POOL_ID,
        app_client_id=testing.mlflow_server.FAKE_COGNITO_APP_CLIENT_ID,
        app_client_secret=testing.mlflow_server.FAKE_COGNITO_APP_CLIENT_SECRET,
    )
    jwks = testing.mlflow_server.FakeJWKS.create()
    return _verifier.TokenVerifier(
        cognito=cognito,
        jwks=jwks,
    )


class TestTokenVerifier:
    @pytest.mark.parametrize(
        ("current_time", "token", "expected"),
        [
            (
                testing.mlflow_server.NON_EXPIRED_DATETIME,
                testing.mlflow_server.FAKE_JWT,
                None,
            ),
            (
                testing.mlflow_server.EXPIRED_DATETIME,
                testing.mlflow_server.FAKE_JWT,
                exceptions.TokenExpiredException(),
            ),
            (
                testing.mlflow_server.NON_EXPIRED_DATETIME,
                testing.mlflow_server.FAKE_JWT_INVALID_SIGNATURE,
                exceptions.InvalidSignatureException(),
            ),
            (
                testing.mlflow_server.NON_EXPIRED_DATETIME,
                testing.mlflow_server.FAKE_JWT_INVALID_CLIENT_ID,
                # Currently unable to test for the expected dedicated exception
                # (`exceptions.InvalidClientException`) since it seems to be
                # impossible to change the payload without breaking the
                # signature.
                exceptions.InvalidSignatureException(),
            ),
            (
                testing.mlflow_server.NON_EXPIRED_DATETIME,
                testing.mlflow_server.FAKE_JWT_INVALID_ISSUER,
                # See above, dedicated exception here is
                # `exceptions.InvalidIssuerException`
                exceptions.InvalidSignatureException(),
            ),
            (
                testing.mlflow_server.NON_EXPIRED_DATETIME,
                testing.mlflow_server.FAKE_JWT_INVALID_TOKEN_TYPE,
                # See above, dedicated exception here is
                # `exceptions.IncorrectTokenTypeException`
                exceptions.InvalidSignatureException(),
            ),
        ],
    )
    def test_verify_token(
        self, expect_raise_if_exception, verifier, current_time, token, expected
    ):
        with freezegun.freeze_time(current_time):
            with expect_raise_if_exception(expected):
                verifier.verify_token(token)
