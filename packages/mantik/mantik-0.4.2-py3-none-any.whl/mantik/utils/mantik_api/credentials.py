import dataclasses
import typing as t

import mantik.utils.env as env

_MANTIK_USERNAME_ENV_VAR = "MANTIK_USERNAME"
_MANTIK_PASSWORD_ENV_VAR = "MANTIK_PASSWORD"


@dataclasses.dataclass(repr=False, frozen=True)
class Credentials:
    """Holds the credentials for authentication."""

    username: str
    password: str

    @classmethod
    def from_env(cls) -> "Credentials":
        """Create from environment variables."""
        username = env.get_required_env_var(_MANTIK_USERNAME_ENV_VAR)
        password = env.get_required_env_var(_MANTIK_PASSWORD_ENV_VAR)
        return cls(
            username=username,
            password=password,
        )

    def __str__(self) -> str:
        """Hide the credentials."""
        return self.__repr__()

    def __repr__(self) -> str:
        """Hide the credentials."""
        return f"{self.__class__.__name__}(<masked>)"

    def to_dict(self, include_password: bool = True) -> t.Dict:
        """Return as dict.

        Parameters
        ----------
        include_password : bool, default=True
            Whether to include the password in the result.

        """
        d = dataclasses.asdict(self)

        if include_password:
            return d

        d.pop("password")
        return d
