import dataclasses
import typing as t
import uuid

import jose.jwt

import mantik
import mantik.utils.mantik_api.client as mantik_api

_USERNAME_ENV_VAR = "MANTIK_UNICORE_USERNAME"
_PASSWORD_ENV_VAR = "MANTIK_UNICORE_PASSWORD"


@dataclasses.dataclass
class UnicoreCredentials:
    username: str
    password: str

    @classmethod
    def get_credentials(
        cls,
        connection_id: t.Optional[uuid.UUID] = None,
    ) -> "UnicoreCredentials":
        if connection_id:
            return cls._credentials_from_api(connection_id=connection_id)
        return cls._credentials_from_env_vars()

    @classmethod
    def _credentials_from_api(
        cls,
        connection_id: uuid.UUID,
    ) -> "UnicoreCredentials":
        access_token = mantik.authentication.auth.get_valid_access_token()
        user_id = _get_sub_from_token(access_token)
        connection = mantik_api.get_connection(
            user_id=uuid.UUID(user_id),
            connection_id=connection_id,
            token=access_token,
        )
        return cls(username=connection.login_name, password=connection.password)

    @classmethod
    def _credentials_from_env_vars(cls) -> "UnicoreCredentials":
        username = mantik.utils.env.get_required_env_var(_USERNAME_ENV_VAR)
        password = mantik.utils.env.get_required_env_var(_PASSWORD_ENV_VAR)
        return cls(username=username, password=password)


def _get_sub_from_token(token: str):
    # The `sub` field of the token claims contains the user UUID.
    return jose.jwt.get_unverified_claims(token)["sub"]
