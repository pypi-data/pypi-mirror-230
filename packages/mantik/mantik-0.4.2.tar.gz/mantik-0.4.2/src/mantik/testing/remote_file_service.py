import datetime
import logging
import typing as t
import uuid

import mantik.remote_file_service.abstract_file_service as abc_fs
import mantik.remote_file_service.unicore_file_service as uc_fs

logger = logging.getLogger()

fake_meta = abc_fs.FileMeta(
    owner="FAKE-OWNER", mode="XXX", last_changed=datetime.datetime(2022, 2, 1)
)

fake_file = abc_fs.File(
    path="remote:/fake-dir/fake.file",
    metadata=fake_meta,
    is_remote=True,
)


fake_directory = abc_fs.Directory(
    path="remote:/fake-dir",
    metadata=fake_meta,
    children=[
        abc_fs.Directory(
            path="remote:/fake-dir/fake-child-dir",
            metadata=fake_meta,
            is_remote=True,
            children=[],
        ),
        fake_file,
    ],
    is_remote=True,
)


class FakeUnicoreFileService(uc_fs.UnicoreFileService):
    def __init__(self):
        pass

    def list_directory(
        self, target
    ) -> t.List[t.Union[abc_fs.Directory, abc_fs.File]]:
        logger.debug(f"list_directory {target}")
        return fake_directory.children

    def create_directory(self, target) -> abc_fs.Directory:
        logger.debug(f"create_directory {target}")
        return fake_directory

    def remove_directory(self, target) -> None:
        logger.debug(f"remove_directory {target}")
        pass

    def copy_directory(
        self,
        source,
        target,
    ) -> abc_fs.Directory:
        logger.debug(f"copy_directory {source} {target}")
        return fake_directory

    def create_file_if_not_exists(self, target) -> abc_fs.File:
        logger.debug(f"create_file_if_not_exists {target}")
        return fake_file

    def remove_file(self, target) -> None:
        logger.debug(f"remove_file {target}")

    def copy_file(self, source, target) -> abc_fs.File:
        logger.debug(f"copy_file {source} {target}")
        return fake_file

    def exists(self, path) -> bool:
        return True

    @property
    def user(self) -> str:
        return "FAKE-USER"

    def change_permissions(self, target, new_permissions) -> None:
        pass

    @classmethod
    def from_env(cls, connection_id: t.Optional[uuid.UUID] = None):
        pass
