import dataclasses
import pathlib
import typing as t


@dataclasses.dataclass
class AddDataRepositoryModel:
    uri: str
    data_repository_name: t.Optional[str] = None
    access_token: t.Optional[str] = None
    description: t.Optional[str] = None

    @classmethod
    def from_target(
        cls,
        target: t.Union[str, pathlib.Path],
        user: str,
        mantik_name: t.Optional[str],
        mantik_description: t.Optional[str],
    ):
        return cls(
            uri=str(target),
            data_repository_name=mantik_name if mantik_name else str(target),
            description=mantik_description
            if mantik_description
            else (
                f"This data repository with path: {str(target)} "
                f"was uploaded by {user}"
            ),
        )

    def to_dict(self) -> t.Dict:
        return {
            "dataRepositoryName": self.data_repository_name,
            "uri": self.uri,
            "accessToken": self.access_token,
            "description": self.description,
        }
