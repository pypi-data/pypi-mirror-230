import io
import logging
import pathlib
import typing as t
import uuid

import fs.copy
import fs.errors
import fs.ftpfs
import pyunicore.credentials
import pyunicore.uftpfs as uc_uftpfs

import mantik.authentication.auth
import mantik.remote_file_service.abstract_file_service as abstract_file_service  # noqa
import mantik.unicore.config.core as core
import mantik.unicore.credentials as _unicore_credentials

logger = logging.getLogger()

FilePath = abstract_file_service.FilePath


def join(path_1: FilePath, path_2: FilePath) -> FilePath:
    return str(pathlib.Path(path_1).joinpath(pathlib.Path(path_2)))


def is_remote(path: FilePath) -> bool:
    return path.startswith("remote:")


def localise_path(path: FilePath) -> FilePath:
    return path.replace("remote:", "")


class UnicoreFileService(abstract_file_service.AbstractFileService):
    """Client that allows transferring files between unicore and
    the local machine.

    To specify that a path is remote, start the path with `remote:`
    E.g. `client.copy_file("/path/local.file", "remote:/path/local.file")`
    This would upload the file from local to unicore.

    Permission handling is not supported here, as it's not implemented by
    pyunicore. This includes viewing the file mode, and file owner.
    """

    def __init__(
        self,
        username: str,
        password: str,
        auth_url: str,
        remote_base_path: str = "/",
        local_base_path: str = ".",
    ):
        self.username = username
        self.remote_fs = uc_uftpfs.UFTPFS(
            auth_url=auth_url,
            creds=pyunicore.credentials.UsernamePassword(username, password),
            base_path=remote_base_path,
        )
        self.local_fs = fs.open_fs(local_base_path)

    def copy_file(
        self,
        source: FilePath,
        target: FilePath,
    ) -> abstract_file_service.File:
        (
            source_fs,
            relative_source_path,
        ) = self._get_current_fs_and_relative_filepath(source)
        (
            target_fs,
            relative_target_path,
        ) = self._get_current_fs_and_relative_filepath(target)

        fs.copy.copy_file(
            src_fs=source_fs,
            src_path=relative_source_path,
            dst_fs=target_fs,
            dst_path=relative_target_path,
        )

        return self._get_file_details(target)

    def remove_file(self, target=FilePath) -> None:
        current_fs, relative_path = self._get_current_fs_and_relative_filepath(
            target
        )
        current_fs.remove(relative_path)

    def _get_current_fs_and_relative_filepath(self, path: FilePath):
        current_fs = self.remote_fs if is_remote(path) else self.local_fs
        relative_path = localise_path(path) if is_remote(path) else path

        return current_fs, relative_path

    def create_file_if_not_exists(
        self, target=FilePath
    ) -> abstract_file_service.File:
        if not self.exists(target):
            if is_remote(target):
                with io.BytesIO() as file:
                    self.remote_fs.upload(localise_path(target), file)
            else:
                self.local_fs.create(target)
        return self._get_file_details(target)

    def _get_file_details(self, path: FilePath) -> abstract_file_service.File:
        current_fs, relative_path = self._get_current_fs_and_relative_filepath(
            path
        )

        return abstract_file_service.File(
            path=path,
            is_remote=is_remote(path),
            metadata=abstract_file_service.FileMeta(
                owner=self.user,
                last_changed=current_fs.getmodified(relative_path),
                mode="Unknown",  # Note: Not supported by pyunicore
            ),
        )

    def _get_directory_details(
        self, path: FilePath, fill_children: bool = False
    ) -> abstract_file_service.Directory:
        current_fs, relative_path = self._get_current_fs_and_relative_filepath(
            path
        )

        if fill_children:
            children = []
            directory_contents = current_fs.listdir(relative_path)

            for item in directory_contents:
                if current_fs.getdetails(join(relative_path, item)).is_dir:
                    children.append(
                        self._get_directory_details(join(path, item))
                    )
                else:
                    children.append(self._get_file_details(join(path, item)))

        else:
            children = []

        return abstract_file_service.Directory(
            path=path,
            is_remote=is_remote(path),
            metadata=abstract_file_service.FileMeta(
                owner="Unknown",  # Note: Not supported by pyunicore
                last_changed=current_fs.getmodified(relative_path),
                mode="Unknown",  # Note: Not supported by pyunicore
            ),
            children=children,
        )

    def list_directory(
        self, target: FilePath
    ) -> t.List[
        t.Union[abstract_file_service.Directory, abstract_file_service.File]
    ]:
        return self._get_directory_details(
            path=target, fill_children=True
        ).children

    def create_directory(
        self, target: FilePath
    ) -> abstract_file_service.Directory:
        current_fs, relative_path = self._get_current_fs_and_relative_filepath(
            target
        )
        current_fs.makedir(relative_path)

        return self._get_directory_details(path=target, fill_children=False)

    def remove_directory(self, target: FilePath) -> None:
        current_fs, relative_path = self._get_current_fs_and_relative_filepath(
            target
        )
        current_fs.removetree(relative_path)

    def copy_directory(
        self, source: FilePath, target: FilePath
    ) -> abstract_file_service.Directory:
        self._copy_dir(source, target)
        return self._get_directory_details(path=target, fill_children=True)

    @property
    def user(self) -> str:
        return self.username

    def change_permissions(
        self, target: FilePath, new_permissions: abstract_file_service.FileMeta
    ) -> None:
        # Note: Not supported by pyunicore
        raise NotImplementedError()

    def exists(self, path=FilePath) -> bool:
        current_fs, relative_path = self._get_current_fs_and_relative_filepath(
            path
        )
        try:
            return current_fs.exists(relative_path)
        except fs.errors.PermissionDenied:
            return False

    def _copy_dir(
        self,
        source_path: FilePath,
        target_path: FilePath,
    ):
        """
        Function which copies one directory to another, compatible with
        pyunicore uftpfs.

        This custom function is needed because of an incompatability
        between pyfilesystem and pyunicore uftpfs. Upon using the default
        copy dir, the filesystem is checked for the existence of the target dir.
        If the target dir doesn't exist, and the target filesystem is uftpfs,
        this results in a permission denied rather than 'does not exist',
        which crashes the request.
        """
        if not self.exists(target_path):
            logger.info(f"mkdir: {target_path}")
            self.create_directory(target_path)

        (
            source_fs,
            relative_source_path,
        ) = self._get_current_fs_and_relative_filepath(source_path)

        for current_item in source_fs.scandir(relative_source_path):
            current_source_file_path = join(source_path, current_item.name)
            current_target_file_path = join(target_path, current_item.name)
            if current_item.is_dir:
                self._copy_dir(
                    current_source_file_path, current_target_file_path
                )
            else:
                logger.info(
                    f"{current_source_file_path} -> {current_target_file_path}"
                )
                self.copy_file(
                    current_source_file_path, current_target_file_path
                )

    @classmethod
    def from_env(
        cls, connection_id: t.Optional[uuid.UUID] = None
    ) -> "UnicoreFileService":
        unicore_credentials = (
            _unicore_credentials.UnicoreCredentials.get_credentials(
                connection_id
            )
        )
        auth_url = mantik.utils.env.get_required_env_var(
            core._UNICORE_AUTH_SERVER_URL_ENV_VAR
        )

        remote_base_path = (
            mantik.utils.env.get_optional_env_var(
                abstract_file_service.REMOTE_FS_BASE_PATH_ENV_VAR
            )
            or "/"
        )
        local_base_path = (
            mantik.utils.env.get_optional_env_var(
                abstract_file_service.LOCAL_FS_BASE_PATH_ENV_VAR
            )
            or "."
        )

        return cls(
            username=unicore_credentials.username,
            password=unicore_credentials.password,
            auth_url=auth_url,
            remote_base_path=remote_base_path,
            local_base_path=local_base_path,
        )
