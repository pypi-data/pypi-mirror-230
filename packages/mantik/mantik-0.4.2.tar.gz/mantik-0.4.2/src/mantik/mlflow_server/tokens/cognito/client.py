import dataclasses
import logging
import typing as t

import mantik.utils.env as env


logger = logging.getLogger(__name__)

COGNITO_IDP_URL = "https://cognito-idp.{region}.amazonaws.com/{user_pool_id}"
COGNITO_REGION_ENV_VAR = "COGNITO_REGION"
COGNITO_USER_POOL_ID_ENV_VAR = "COGNITO_USER_POOL_ID"
COGNITO_APP_CLIENT_ID_ENV_VAR = "COGNITO_APP_CLIENT_ID"
COGNITO_APP_CLIENT_SECRET_ENV_VAR = "COGNITO_APP_CLIENT_SECRET"


@dataclasses.dataclass
class Properties:
    """The required Cognito User Pool client properties."""

    region: str
    user_pool_id: str
    app_client_id: str
    app_client_secret: t.Optional[str]

    @classmethod
    def from_env(cls, secret_required: bool = True) -> "Properties":
        """Construct from environment variables.

        Parameters
        ----------
        secret_required : bool, default=True
            Whether the app client secret is required.
            It is required to issue tokens from the client API.
            It is not required for authenticating tokens.

        """
        return cls(
            region=env.get_required_env_var(COGNITO_REGION_ENV_VAR),
            user_pool_id=env.get_required_env_var(COGNITO_USER_POOL_ID_ENV_VAR),
            app_client_id=env.get_required_env_var(
                COGNITO_APP_CLIENT_ID_ENV_VAR
            ),
            app_client_secret=_read_app_client_secret_from_env_var(
                required=secret_required
            ),
        )

    @property
    def jwks_file_url(self) -> str:
        """Return the JWKS file URL."""
        return f"{self.idp_url}/.well-known/jwks.json"

    @property
    def idp_url(self) -> str:
        """Return the respective IDP URL."""
        return COGNITO_IDP_URL.format(
            region=self.region,
            user_pool_id=self.user_pool_id,
        )


def _read_app_client_secret_from_env_var(required: bool) -> t.Optional[str]:
    if required:
        return env.get_required_env_var(COGNITO_APP_CLIENT_SECRET_ENV_VAR)
    return env.get_optional_env_var(COGNITO_APP_CLIENT_SECRET_ENV_VAR)
