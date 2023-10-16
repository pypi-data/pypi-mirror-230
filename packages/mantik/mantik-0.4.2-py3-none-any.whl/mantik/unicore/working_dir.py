import logging
import pathlib
import typing as t

import pyunicore.client

logger = logging.getLogger(__name__)


class File:
    """A file in a working directory of a `Job`.

    Wrapper class around pyunicore.client.PathFile.

    """

    def __init__(self, pyunicore_path_file: pyunicore.client.PathFile):
        self._file = pyunicore_path_file

    @property
    def content(self) -> str:
        """Return the file's content."""
        return self._file.raw().read()

    def download(self, local_path: pathlib.Path = pathlib.Path(".")):
        """Download the file.

        Parameters
        ----------
        local_path : pathlib.Path, defaults to "."
            Local path where to save the files.
            By default, the files will be saved to current
            directory.

        """
        _download_file(self._file, local_path=local_path)


class Directory:
    """A sub working directory of a `Job`.

    Wrapper class around pyunicore.client.PathDir.

    """

    def __init__(self, pyunicore_path_dir: pyunicore.client.PathDir):
        self._directory = pyunicore_path_dir

    @property
    def path(self) -> str:
        return self._directory.name

    def download(self, local_path: pathlib.Path = pathlib.Path(".")) -> None:
        """Download the directory to the local file system.

        Parameters
        ----------
        local_path : pathlib.Path, defaults to "."
            Local path where to save the files.
            By default, the files will be saved to current
            directory.

        """
        logger.debug("Downloading directory %s", self.path)
        _download_directory(self._directory, local_path=local_path)


def _download_directory(
    directory: pyunicore.client.PathDir, local_path: pathlib.Path
) -> None:
    content = directory.storage.listdir(base=directory.name)
    logger.debug(f"Directory {directory.name} content: {content}")
    _download_directory_content(content, local_path=local_path)


def _download_directory_content(
    content: dict, local_path: pathlib.Path
) -> None:
    for obj in content.values():
        if _is_directory(obj):
            _download_directory(obj, local_path=local_path)
        else:
            _download_file(obj, local_path=local_path)


def _is_directory(obj: t.Any) -> bool:
    return isinstance(obj, pyunicore.client.PathDir)


def _download_file(
    obj: pyunicore.client.PathFile, local_path: pathlib.Path
) -> None:
    name = local_path / obj.name
    local_path.mkdir(parents=True, exist_ok=True)
    logger.debug("Saving file %s to %s", obj.name, name)
    obj.download(name)


class WorkingDirectory:
    """A working directory of a `Job`,
    wrapper class around pyunicore.client.Storage"""

    def __init__(self, storage: pyunicore.client.Storage):
        self._storage = storage

    def get_directory_or_file(
        self, path: pathlib.Path
    ) -> t.Union[Directory, File]:
        pyunicore_file_or_dir = self._open_path(path)
        if isinstance(pyunicore_file_or_dir, pyunicore.client.PathDir):
            return Directory(pyunicore_file_or_dir)
        elif isinstance(pyunicore_file_or_dir, pyunicore.client.PathFile):
            return File(pyunicore_file_or_dir)
        raise RuntimeError(f"{pyunicore_file_or_dir} not a valid path")

    def _open_path(
        self, path: pathlib.Path
    ) -> t.Union[pyunicore.client.PathFile, pyunicore.client.PathDir]:
        path_str = path.as_posix()
        try:
            pyunicore_object = self._storage.stat(path_str)
        except Exception as e:  # noqa: B902
            raise FileNotFoundError(f"{path} does not exist") from e
        return pyunicore_object

    def get_entire_storage(
        self,
    ) -> t.List[t.Union[pyunicore.client.PathFile, pyunicore.client.PathDir]]:
        """Get list pyunicore.client.PathFile or pyunicore.client.PathDir
        of all files and dir in the pyunicore.client.Storage at path "/" """
        return [
            self._storage.listdir()[path] for path in self._storage.listdir()
        ]
