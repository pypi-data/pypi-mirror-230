import typing as t
import uuid

import mantik.authentication.auth
import mantik.remote_file_service.abstract_file_service as afs
import mantik.remote_file_service.s3_file_service as s3_file_service
import mantik.remote_file_service.unicore_file_service as unicore_file_service
import mantik.utils.mantik_api.client as mantik_api
import mantik.utils.mantik_api.data_repository as data_repository

_PROJECT_ID_ENV_VAR = "PROJECT_ID"

FS_SUPPORTED_TYPES = {
    "UNICORE": unicore_file_service.UnicoreFileService,
    "S3": s3_file_service.S3FileService,
}


class DataClientException(Exception):
    pass


class DataClient(afs.AbstractFileService):
    def __init__(
        self,
        project_id: t.Union[str, uuid.UUID],
        file_service: afs.AbstractFileService,
    ):
        self.access_token = mantik.authentication.auth.get_valid_access_token()
        self.project_id = _str_or_uuid_to_uuid(project_id)
        self.file_service = file_service

    @classmethod
    def from_env(
        cls,
        connection_id: t.Optional[uuid.UUID] = None,
        remote_fs_type: t.Optional[t.Type[afs.AbstractFileService]] = None,
    ) -> "DataClient":
        if remote_fs_type is None:
            remote_fs_type_from_env = mantik.utils.env.get_required_env_var(
                afs.REMOTE_FS_TYPE_ENV_VAR
            )

            try:
                remote_fs_type = FS_SUPPORTED_TYPES[remote_fs_type_from_env]
            except KeyError:
                raise DataClientException(
                    "Invalid remote file system type, set REMOTE_FS_TYPE"
                    f"as one of this supported types {list(FS_SUPPORTED_TYPES.keys())}"  # noqa
                )

        return cls(
            project_id=_str_or_uuid_to_uuid(
                mantik.utils.env.get_required_env_var(_PROJECT_ID_ENV_VAR)
            ),
            file_service=remote_fs_type.from_env(connection_id=connection_id),
        )

    def list_directory(
        self, target: afs.FilePath
    ) -> t.List[t.Union[afs.Directory, afs.File]]:
        return self.file_service.list_directory(target)

    def create_directory(
        self,
        target: afs.FilePath,
        mantik_name: t.Optional[str] = None,
        mantik_description: t.Optional[str] = None,
    ) -> afs.Directory:
        directory = self.file_service.create_directory(target)

        self._create_data_reference(
            data_repository.AddDataRepositoryModel.from_target(
                target=target,
                user=self.user,
                mantik_name=mantik_name,
                mantik_description=mantik_description,
            )
        )

        return directory

    def remove_directory(
        self,
        target: afs.FilePath,
        data_repository_id: t.Optional[t.Union[str, uuid.UUID]] = None,
        data_repository_name: t.Optional[str] = None,
    ) -> None:
        self._delete_data_reference(
            data_repository_id=data_repository_id,
            data_repository_name=data_repository_name,
        )
        self.file_service.remove_directory(target)

    def copy_directory(
        self,
        source: afs.FilePath,
        target: afs.FilePath,
        mantik_name: t.Optional[str] = None,
        mantik_description: t.Optional[str] = None,
    ) -> afs.Directory:
        directory = self.file_service.copy_directory(source, target)

        self._create_data_reference(
            data_repository.AddDataRepositoryModel.from_target(
                target=target,
                user=self.user,
                mantik_name=mantik_name,
                mantik_description=mantik_description,
            )
        )

        return directory

    def create_file_if_not_exists(
        self,
        target=afs.FilePath,
        mantik_name: t.Optional[str] = None,
        mantik_description: t.Optional[str] = None,
    ) -> afs.File:
        file = self.file_service.create_file_if_not_exists(target)

        self._create_data_reference(
            data_repository.AddDataRepositoryModel.from_target(
                target=target,
                user=self.user,
                mantik_name=mantik_name,
                mantik_description=mantik_description,
            )
        )
        return file

    def remove_file(
        self,
        target: afs.FilePath,
        data_repository_id: t.Optional[t.Union[str, uuid.UUID]] = None,
        data_repository_name: t.Optional[str] = None,
    ) -> None:
        self._delete_data_reference(
            data_repository_id=data_repository_id,
            data_repository_name=data_repository_name,
        )
        self.file_service.remove_file(target)

    def copy_file(
        self,
        source: afs.FilePath,
        target: afs.FilePath,
        mantik_name: t.Optional[str] = None,
        mantik_description: t.Optional[str] = None,
    ) -> afs.File:
        file = self.file_service.copy_file(source, target)

        self._create_data_reference(
            data_repository.AddDataRepositoryModel.from_target(
                target=target,
                user=self.user,
                mantik_name=mantik_name,
                mantik_description=mantik_description,
            )
        )

        return file

    @property
    def user(self) -> str:
        return self.file_service.user

    def change_permissions(
        self, target: afs.FilePath, new_permissions: afs.FileMeta
    ) -> None:
        self.file_service.change_permissions(target, new_permissions)

    def _create_data_reference(
        self,
        add_data_repository: data_repository.AddDataRepositoryModel,
    ):
        try:
            data_repository_id = mantik_api.create_data_repository(
                add_data_repository=add_data_repository,
                project_id=self.project_id,
                token=self.access_token,
            )
        except Exception as e:
            raise DataClientException(
                "During the creation of a new data repository,"
                f"the following error occurred: {str(e)}\n"
                "The data has been anyway "
                "successfully transferred remotely."
            )
        return data_repository_id

    def _delete_data_reference(
        self,
        data_repository_id: t.Optional[t.Union[str, uuid.UUID]] = None,
        data_repository_name: t.Optional[str] = None,
    ):
        if data_repository_id:
            data_repository_id = _str_or_uuid_to_uuid(data_repository_id)
            mantik_api.delete_data_repository(
                project_id=self.project_id,
                data_repository_id=data_repository_id,
                token=self.access_token,
            )
            return None
        if data_repository_name:
            for data_repo in mantik_api.get_data_repositories(
                self.project_id, self.access_token
            ):
                if data_repo.get("dataRepositoryName") == data_repository_name:
                    mantik_api.delete_data_repository(
                        project_id=self.project_id,
                        data_repository_id=uuid.UUID(
                            data_repo["dataRepositoryId"]
                        ),
                        token=self.access_token,
                    )
                    return None
            raise DataClientException(
                f"A data repository with name: "
                f"{data_repository_name} was not found.\n"
                "Make sure that the name is correct and "
                "that the repository has not been deleted already.\n"
                "To solve the problem, consider passing 'data_repository_id'."
            )
        raise DataClientException(
            "Either 'data_repository_id' or 'data_repository_name' "
            "must be passed as arguments, "
            "in order to delete the associated data repository in Mantik.\n"
            "If no reference is present use the FileService directly."
        )


def _str_or_uuid_to_uuid(id_: t.Union[str, uuid.UUID]):
    if isinstance(id_, str):
        try:
            id_ = uuid.UUID(id_)
        except ValueError:
            raise DataClientException(
                "Badly formed hexadecimal UUID string for project ID"
            )
    return id_
