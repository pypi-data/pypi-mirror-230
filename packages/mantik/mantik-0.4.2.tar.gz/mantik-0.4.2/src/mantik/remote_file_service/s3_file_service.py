import dataclasses
import logging
import typing as t
import uuid

import fs.copy
import fs_s3fs
import jose.jwt

import mantik.authentication
import mantik.remote_file_service.abstract_file_service as afs  # noqa
import mantik.utils
import mantik.utils.mantik_api.client as mantik_api

logger = logging.getLogger()

FilePath = afs.FilePath


def is_remote(path: FilePath) -> bool:
    """Checks whether a given url is an S3 url."""
    return path.startswith("s3://")


def localise_path(path: FilePath) -> FilePath:
    """Strips s3 prefix and bucket name from S3 url."""
    bucket_name = get_bucket_name(path)
    remainder = path.replace(f"s3://{bucket_name}", "")
    if remainder.startswith("/"):
        return remainder[1::]
    return remainder


def get_bucket_name(path: FilePath) -> str:
    """Extracts bucket name from an S3 url `s3://<bucket-name>/resource/...`"""
    if not is_remote(path):
        raise ValueError("Not an s3 url.")

    path_without_prefix = path.replace("s3://", "")
    return path_without_prefix.split("/")[0]


class S3FileService(afs.AbstractFileService):
    """Client that allows transferring files between s3 and
    the local machine.

    To specify that a path is remote, start the path with `s3://`
    E.g. `client.copy_file("/path/local.file", "s3://path/local.file")`
    This would upload the file from local to s3.
    """

    def __init__(
        self,
        aws_access_key_id: str,
        aws_secret_access_key: str,
        local_base_path: str = ".",
    ):
        self.local_fs = fs.open_fs(local_base_path)
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key

    def copy_file(
        self,
        source: FilePath,
        target: FilePath,
    ) -> afs.File:
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

    def create_file_if_not_exists(self, target=FilePath) -> afs.File:
        current_fs, local_path = self._get_current_fs_and_relative_filepath(
            target
        )
        current_fs.create(local_path, wipe=False)
        return self._get_file_details(target)

    def list_directory(
        self, target: FilePath
    ) -> t.List[t.Union[afs.Directory, afs.File]]:
        return self._get_directory_details(
            path=target, fill_children=True
        ).children

    def create_directory(self, target: FilePath) -> afs.Directory:
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
    ) -> afs.Directory:
        src_fs, src_path = self._get_current_fs_and_relative_filepath(source)
        dst_fs, dst_path = self._get_current_fs_and_relative_filepath(target)

        fs.copy.copy_dir(
            src_fs=src_fs, src_path=src_path, dst_fs=dst_fs, dst_path=dst_path
        )
        return self._get_directory_details(path=target, fill_children=True)

    @property
    def user(self) -> str:
        return self.aws_access_key_id

    def change_permissions(
        self, target: FilePath, new_permissions: afs.FileMeta
    ) -> None:
        raise NotImplementedError()

    def exists(self, path=FilePath) -> bool:
        current_fs, relative_path = self._get_current_fs_and_relative_filepath(
            path
        )
        try:
            return current_fs.exists(relative_path)
        except fs.errors.PermissionDenied:
            return False

    def _get_directory_details(
        self, path: FilePath, fill_children: bool = False
    ) -> afs.Directory:
        current_fs, relative_path = self._get_current_fs_and_relative_filepath(
            path
        )

        if fill_children:
            children = []
            directory_contents = current_fs.listdir(relative_path)
            for item in directory_contents:
                if current_fs.getdetails(
                    fs.path.combine(relative_path, item)
                ).is_dir:
                    children.append(
                        self._get_directory_details(fs.path.combine(path, item))
                    )
                else:
                    children.append(
                        self._get_file_details(fs.path.combine(path, item))
                    )

        else:
            children = []

        return afs.Directory(
            path=path,
            is_remote=is_remote(path),
            metadata=afs.FileMeta(
                owner="Unknown",
                last_changed=current_fs.getmodified(relative_path),
                mode="Unknown",
            ),
            children=children,
        )

    def _get_file_details(self, path: FilePath) -> afs.File:
        current_fs, relative_path = self._get_current_fs_and_relative_filepath(
            path
        )

        return afs.File(
            path=path,
            is_remote=is_remote(path),
            metadata=afs.FileMeta(
                owner=self.user,
                last_changed=current_fs.getmodified(relative_path),
                mode="Unknown",  # Note: Not supported by python fs
            ),
        )

    def _get_current_fs_and_relative_filepath(self, path: FilePath):
        current_fs = (
            self._get_s3_fs(bucket_name=get_bucket_name(path))
            if is_remote(path)
            else self.local_fs
        )
        relative_path = localise_path(path) if is_remote(path) else path

        return current_fs, relative_path

    def _get_s3_fs(self, bucket_name: str) -> fs_s3fs.S3FS:
        return fs_s3fs.S3FS(
            bucket_name=bucket_name,
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key,
        )

    @classmethod
    def from_env(
        cls, connection_id: t.Optional[uuid.UUID] = None
    ) -> "S3FileService":
        s3_credentials = S3Credentials.get_credentials(
            connection_id=connection_id
        )

        local_base_path = (
            mantik.utils.env.get_optional_env_var(
                afs.LOCAL_FS_BASE_PATH_ENV_VAR
            )
            or "."
        )

        return cls(
            aws_access_key_id=s3_credentials.aws_access_key_id,
            aws_secret_access_key=s3_credentials.aws_secret_access_key,
            local_base_path=local_base_path,
        )


_USERNAME_ENV_VAR = "AWS_ACCESS_KEY_ID"
_PASSWORD_ENV_VAR = "AWS_SECRET_ACCESS_KEY"


@dataclasses.dataclass
class S3Credentials:
    aws_access_key_id: str
    aws_secret_access_key: str

    @classmethod
    def get_credentials(
        cls,
        connection_id: t.Optional[uuid.UUID] = None,
    ) -> "S3Credentials":
        if connection_id:
            return cls._credentials_from_api(connection_id=connection_id)
        return cls._credentials_from_env_vars()

    @classmethod
    def _credentials_from_api(
        cls,
        connection_id: uuid.UUID,
    ) -> "S3Credentials":
        access_token = mantik.authentication.auth.get_valid_access_token()
        user_id = _get_sub_from_token(access_token)
        connection = mantik_api.get_connection(
            user_id=uuid.UUID(user_id),
            connection_id=connection_id,
            token=access_token,
        )
        return cls(
            aws_access_key_id=connection.login_name,
            aws_secret_access_key=connection.password,
        )

    @classmethod
    def _credentials_from_env_vars(cls) -> "S3Credentials":
        username = mantik.utils.env.get_required_env_var(_USERNAME_ENV_VAR)
        password = mantik.utils.env.get_required_env_var(_PASSWORD_ENV_VAR)
        return cls(aws_access_key_id=username, aws_secret_access_key=password)


def _get_sub_from_token(token: str):
    # The `sub` field of the token claims contains the user UUID.
    return jose.jwt.get_unverified_claims(token)["sub"]
