import datetime
import uuid

import pytest
import requests_mock

import mantik.remote_file_service.abstract_file_service as afs
import mantik.remote_file_service.data_client as _data_client
import mantik.utils.mantik_api.client as mantik_api


class TestDataClient:
    def test_list_directory(self, data_client, fake_unicore_fs):
        target = "test_target"
        assert data_client.list_directory(
            target
        ) == fake_unicore_fs.list_directory(target)

    def test_create_directory(self, data_client, fake_unicore_fs, project_id):
        with requests_mock.Mocker() as m:
            m.post(
                url=f"{mantik_api._DEFAULT_MANTIK_API_URL}/mantik-api/"
                f"projects/{str(project_id)}/data",
                json={
                    "dataRepositoryId": str(uuid.uuid4()),
                },
            )
            target = "test_target"
            mantik_name = ""
            mantik_description = ""
            assert data_client.create_directory(
                target,
                mantik_name=mantik_name,
                mantik_description=mantik_description,
            ) == fake_unicore_fs.create_directory(target)
            assert m.request_history[0].json() == {
                "accessToken": None,
                "dataRepositoryName": "test_target",
                "description": "This data repository with "
                "path: test_target was uploaded by FAKE-USER",
                "uri": "test_target",
            }

    def test_remove_directory(self, data_client, fake_unicore_fs, project_id):
        data_repository_id = uuid.uuid4()
        with requests_mock.Mocker() as m:
            m.delete(
                url=f"{mantik_api._DEFAULT_MANTIK_API_URL}/mantik-api/"
                f"projects/{str(project_id)}/data/{data_repository_id}",
                json={
                    "dataRepositoryId": str(uuid.uuid4()),
                },
            )
            target = "test_target"
            assert data_client.remove_directory(
                target, data_repository_id=data_repository_id
            ) == fake_unicore_fs.remove_directory(target)
            assert len(m.request_history) == 1

    def test_copy_directory(self, data_client, fake_unicore_fs, project_id):
        with requests_mock.Mocker() as m:
            m.post(
                url=f"{mantik_api._DEFAULT_MANTIK_API_URL}/mantik-api/"
                f"projects/{str(project_id)}/data",
                json={
                    "dataRepositoryId": str(uuid.uuid4()),
                },
            )
            source = "test_source"
            target = "test_target"
            mantik_name = "test-name"
            mantik_description = ""
            assert data_client.copy_directory(
                source,
                target,
                mantik_name=mantik_name,
                mantik_description=mantik_description,
            ) == fake_unicore_fs.copy_directory(source, target)
            assert m.request_history[0].json() == {
                "accessToken": None,
                "dataRepositoryName": "test-name",
                "description": "This data repository "
                "with path: test_target was uploaded by FAKE-USER",
                "uri": "test_target",
            }

    def test_create_file_if_not_exists(
        self, data_client, fake_unicore_fs, project_id
    ):
        with requests_mock.Mocker() as m:
            m.post(
                url=f"{mantik_api._DEFAULT_MANTIK_API_URL}/mantik-api/"
                f"projects/{str(project_id)}/data",
                json={
                    "dataRepositoryId": str(uuid.uuid4()),
                },
            )
            target = "test_target"
            mantik_name = "test-name"
            mantik_description = "test-description"
            assert data_client.create_file_if_not_exists(
                target,
                mantik_name=mantik_name,
                mantik_description=mantik_description,
            ) == fake_unicore_fs.create_file_if_not_exists(target)
            assert m.request_history[0].json() == {
                "accessToken": None,
                "dataRepositoryName": "test-name",
                "description": "test-description",
                "uri": "test_target",
            }

    def test_remove_file(self, data_client, fake_unicore_fs, project_id):
        data_repository_name = "data-repo-test-name"
        data_repository_id = "3fa85f64-5717-4562-b3fc-2c963f66afa6"
        with requests_mock.Mocker() as m:
            m.get(
                url=f"{mantik_api._DEFAULT_MANTIK_API_URL}/mantik-api/"
                f"projects/{str(project_id)}/data",
                json={
                    "totalRecords": 1,
                    "dataRepositories": [
                        {
                            "dataRepositoryId": "3fa85f64-5717-4562-b3fc-2c963f66afa6",  # noqa
                            "dataRepositoryName": data_repository_name,
                            "uri": "string",
                            "accessToken": "string",
                            "description": "string",
                        }
                    ],
                },
            )
            m.delete(
                url=f"{mantik_api._DEFAULT_MANTIK_API_URL}/mantik-api/projects/"
                f"{str(project_id)}/data/{data_repository_id}",
                json={
                    "dataRepositoryId": str(uuid.uuid4()),
                },
            )
            target = "test_target"
            assert data_client.remove_file(
                target, data_repository_name=data_repository_name
            ) == fake_unicore_fs.remove_file(target)
            assert len(m.request_history) == 2

    def test_copy_file(self, data_client, fake_unicore_fs, project_id):
        with requests_mock.Mocker() as m:
            m.post(
                url=f"{mantik_api._DEFAULT_MANTIK_API_URL}/mantik-api/"
                f"projects/{str(project_id)}/data",
                json={
                    "dataRepositoryId": str(uuid.uuid4()),
                },
            )
            source = "test_source"
            target = "test_target"
            mantik_name = "test-name"
            mantik_description = "test-description"
            assert data_client.copy_file(
                source,
                target,
                mantik_name=mantik_name,
                mantik_description=mantik_description,
            ) == fake_unicore_fs.copy_file(source, target)
            assert m.request_history[0].json() == {
                "accessToken": None,
                "dataRepositoryName": "test-name",
                "description": "test-description",
                "uri": "test_target",
            }

    def test_user(self, data_client, fake_unicore_fs):
        assert data_client.user == fake_unicore_fs.user

    def test_change_permissions(self, data_client, fake_unicore_fs):
        target = "test_target"
        new_permissions = afs.FileMeta(
            last_changed=datetime.datetime(2022, 1, 1),
            mode="xxx",
            owner=fake_unicore_fs.user,
        )
        assert data_client.change_permissions(
            target, new_permissions
        ) == fake_unicore_fs.change_permissions(target, new_permissions)

    def test_remove_file_no_reference(self, data_client, fake_unicore_fs):
        with pytest.raises(_data_client.DataClientException) as e:
            target = "test_target"
            data_client.remove_file(target)
        assert str(e.value) == (
            "Either 'data_repository_id' or "
            "'data_repository_name' must be passed as "
            "arguments, in order to delete "
            "the associated data repository in Mantik.\n"
            "If no reference is present use the FileService directly."
        )

    def test_remove_file_name_not_present(
        self, data_client, fake_unicore_fs, project_id
    ):
        with pytest.raises(_data_client.DataClientException) as e:
            data_repository_name = "not present name"
            with requests_mock.Mocker() as m:
                m.get(
                    url=f"{mantik_api._DEFAULT_MANTIK_API_URL}/mantik-api/"
                    f"projects/{str(project_id)}/data",
                    json={
                        "totalRecords": 1,
                        "dataRepositories": [
                            {
                                "dataRepositoryId": "3fa85f64-5717-4562-b3fc-2c963f66afa6",  # noqa
                                "dataRepositoryName": "name",
                                "uri": "string",
                                "accessToken": "string",
                                "description": "string",
                            }
                        ],
                    },
                )
                target = "test_target"
                data_client.remove_file(
                    target, data_repository_name=data_repository_name
                )
        assert str(e.value) == (
            "A data repository with name: not present name was not found.\n"
            "Make sure that the name is correct and "
            "that the repository has not been "
            "deleted already.\n"
            "To solve the problem, consider passing 'data_repository_id'."
        )

    def test_init_false_project_id(self, env_vars_set):
        with env_vars_set(
            {
                "PROJECT_ID": "error",
                "REMOTE_FS_TYPE": "UNICORE",
            }
        ), pytest.raises(_data_client.DataClientException) as e:
            assert _data_client.DataClient.from_env()

        assert (
            str(e.value)
            == "Badly formed hexadecimal UUID string for project ID"
        )

    def test_init_not_supported_backend(self, env_vars_set):
        with env_vars_set(
            {
                "PROJECT_ID": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "REMOTE_FS_TYPE": "NEW_BACKEND",
            }
        ), pytest.raises(_data_client.DataClientException) as e:
            assert _data_client.DataClient.from_env()

        assert str(e.value) == (
            "Invalid remote file system type, "
            "set REMOTE_FS_TYPEas one of this supported "
            "types ['UNICORE', 'S3']"
        )
