import abc
import dataclasses
import datetime
import pathlib
import typing as t
import uuid

FilePath = t.Union[str, pathlib.Path]

REMOTE_FS_BASE_PATH_ENV_VAR = "MANTIK_REMOTE_FS_BASE_PATH"
LOCAL_FS_BASE_PATH_ENV_VAR = "MANTIK_LOCAL_FS_BASE_PATH"
REMOTE_FS_TYPE_ENV_VAR = "REMOTE_FS_TYPE"


@dataclasses.dataclass
class FileMeta:
    owner: str
    mode: str
    last_changed: datetime.datetime


@dataclasses.dataclass
class File:
    path: FilePath
    metadata: FileMeta
    is_remote: bool


@dataclasses.dataclass
class Directory(File):
    children: t.List[t.Union["Directory", "File"]]


class AbstractFileService(abc.ABC):
    """
    Abstract class to define methods used for (remote) file handling.

    This interface must be easily implementable with common file transfer
    methods (FTP, boto/S3, GNU filesystem, pathlib + python IO ...).
    """

    @abc.abstractmethod
    def list_directory(
        self, target: FilePath
    ) -> t.List[t.Union[Directory, File]]:
        """
        List content of directory.

        Note: bash ls
        """

    @abc.abstractmethod
    def create_directory(self, target: FilePath) -> Directory:
        """
        Make a new directory.

        Note: bash mkdir
        """

    @abc.abstractmethod
    def remove_directory(self, target: FilePath) -> None:
        """Remove a directory.

        Note: bash rm -r
        """

    @abc.abstractmethod
    def copy_directory(
        self,
        source: FilePath,
        target: FilePath,
    ) -> Directory:
        """Copy directory.

        Note: bash cp
        """

    @abc.abstractmethod
    def create_file_if_not_exists(self, target: FilePath) -> File:
        """Create (empty) file if not exists.

        Note: bash touch
        """

    @abc.abstractmethod
    def remove_file(self, target: FilePath) -> None:
        """Remove file or directory.

        Note: bash rm
        """

    @abc.abstractmethod
    def copy_file(
        self,
        source: FilePath,
        target: FilePath,
    ) -> File:
        """Copy file.

        Note: bash cp
        """

    @property
    @abc.abstractmethod
    def user(self) -> str:
        """Return current user."""

    @abc.abstractmethod
    def change_permissions(
        self, target: FilePath, new_permissions: FileMeta
    ) -> None:
        """Change metadata (permissions) of a file.

        Note: bash chmod
        """

    @classmethod
    @abc.abstractmethod
    def from_env(
        cls, connection_id: t.Optional[uuid.UUID] = None
    ) -> "AbstractFileService":
        """Instantiate with environment variables.

        Credentials are either fetched from mantik api
        or passed in through end vars.
        """
