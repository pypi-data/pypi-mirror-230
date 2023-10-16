import dataclasses
import datetime
import json
import logging
import pathlib
import typing as t

logger = logging.getLogger(__name__)


@dataclasses.dataclass(frozen=True)
class Tokens:
    """Holds AWS Cognito auth tokens."""

    access_token: str
    refresh_token: str
    expires_at: datetime.datetime
    __encoding = "utf-8"

    @classmethod
    def from_json_response(
        cls, response: t.Dict, refresh_token: t.Optional[str] = None
    ) -> "Tokens":
        """Create from JSON response."""
        access_token = response["AccessToken"]
        expires_at = datetime.datetime.fromisoformat(response["ExpiresAt"])
        if refresh_token is None:
            refresh_token = response["RefreshToken"]
        return cls(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_at=expires_at,
        )

    @classmethod
    def from_file(cls, path: pathlib.Path) -> "Tokens":
        """Create from a JSON file."""
        with open(path, encoding=cls.__encoding) as f:
            data = json.load(f, object_hook=_deserialize_datetime)
            return cls(**data)

    @property
    def has_expired(self) -> bool:
        """Return whether the token has expired."""
        tz = self.expires_at.tzinfo
        return self.expires_at < datetime.datetime.now(tz=tz)

    def write_to_file(self, path: pathlib.Path) -> None:
        """Write tokens to file."""
        if not path.parent.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
        logger.debug("Writing tokens %s to file %s", self, path.as_posix())
        with open(path, "w", encoding=self.__encoding) as f:
            data = dataclasses.asdict(self)
            json.dump(
                data,
                f,
                ensure_ascii=False,
                default=_serialize_datetime,
            )


def _deserialize_datetime(
    data: t.Dict[str, str]
) -> t.Dict[str, t.Union[str, datetime.datetime]]:
    expires_at_attribute = "expires_at"
    try:
        value = data[expires_at_attribute]
    except KeyError:
        raise KeyError(f"Token file is missing '{expires_at_attribute}' field")
    data[expires_at_attribute] = datetime.datetime.fromisoformat(value)
    return data


def _serialize_datetime(value: t.Any) -> str:
    if isinstance(value, datetime.datetime):
        return value.isoformat()
    return str(value)
