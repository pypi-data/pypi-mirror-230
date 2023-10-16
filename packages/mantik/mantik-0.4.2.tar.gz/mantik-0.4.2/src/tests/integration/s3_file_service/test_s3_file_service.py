import pathlib
import shutil

import boto3
import fs_s3fs
import moto
import pytest

import mantik.remote_file_service.s3_file_service as s3_fs
import mantik.utils.env as env


BUCKET_NAME = "mocked-bucket"

LOCAL_WORKING_DIRECTORY = "src/tests/integration/s3_file_service/workspace"

SAMPLE_FOLDER = "sample-directory"
SAMPLE_FILENAME = "hello-world.txt"
SAMPLE_FILE_FILE_PATH = f"{SAMPLE_FOLDER}/{SAMPLE_FILENAME}"

DOWNLOADS = "downloads"


@pytest.fixture
def mock_s3():
    with moto.mock_s3():
        client = boto3.client("s3")
        client.create_bucket(
            Bucket=BUCKET_NAME,
            CreateBucketConfiguration={"LocationConstraint": "eu-central-1"},
        )

        yield


@pytest.fixture
def mock_s3_with_sample_file(mock_s3):
    client = boto3.client("s3")
    client.upload_file(
        f"{LOCAL_WORKING_DIRECTORY}/{SAMPLE_FILE_FILE_PATH}",
        BUCKET_NAME,
        SAMPLE_FILE_FILE_PATH,
    )
    fs_s3fs.S3FS(
        bucket_name=BUCKET_NAME,
        aws_access_key_id="1234",
        aws_secret_access_key="XXXX",
    ).makedir(
        SAMPLE_FOLDER
    )  # Needed because there is no 'real' concept of folders in S3
    # See: https://github.com/PyFilesystem/s3fs/issues/17
    yield


@pytest.fixture
def temp_testing_folder_path(tmp_path) -> str:
    # Copy the source folder to the temporary directory
    shutil.copytree(
        f"{LOCAL_WORKING_DIRECTORY}/{SAMPLE_FOLDER}", tmp_path / SAMPLE_FOLDER
    )
    # Create a folder to download to, in the new temp directory
    pathlib.Path(tmp_path / DOWNLOADS).mkdir()

    yield str(tmp_path)


@pytest.fixture()
def s3_fs_client(temp_testing_folder_path) -> s3_fs.S3FileService:
    return s3_fs.S3FileService(
        aws_access_key_id="1234",
        aws_secret_access_key="XXXX",
        local_base_path=temp_testing_folder_path,
    )


def test_list_directory(s3_fs_client: s3_fs, mock_s3_with_sample_file) -> None:
    local_list_dir = s3_fs_client.list_directory(SAMPLE_FOLDER)
    assert len(local_list_dir) == 1
    assert local_list_dir[0].path == SAMPLE_FILE_FILE_PATH
    remote_list_dir = s3_fs_client.list_directory(
        f"s3://{BUCKET_NAME}/{SAMPLE_FOLDER}"
    )
    assert len(remote_list_dir) == 1
    assert (
        remote_list_dir[0].path == f"s3://{BUCKET_NAME}/{SAMPLE_FILE_FILE_PATH}"
    )


def test_copy_file_both_ways_works(
    s3_fs_client: s3_fs,
    mock_s3,
) -> None:
    # from local to s3
    assert not s3_fs_client.exists(f"s3://{BUCKET_NAME}/{SAMPLE_FILENAME}")

    s3_fs_client.copy_file(
        f"{SAMPLE_FILE_FILE_PATH}",
        f"s3://{BUCKET_NAME}/{SAMPLE_FILENAME}",
    )
    assert s3_fs_client.exists(f"s3://{BUCKET_NAME}/{SAMPLE_FILENAME}")

    # from s3 to local
    assert not s3_fs_client.exists(f"{DOWNLOADS}/{SAMPLE_FILENAME}")

    s3_fs_client.copy_file(
        f"s3://{BUCKET_NAME}/{SAMPLE_FILENAME}",
        f"{DOWNLOADS}/{SAMPLE_FILENAME}",
    )
    assert s3_fs_client.exists(f"/{DOWNLOADS}/{SAMPLE_FILENAME}")


def test_remove_file(
    s3_fs_client: s3_fs,
    mock_s3_with_sample_file,
) -> None:
    # s3
    assert s3_fs_client.exists(f"s3://{BUCKET_NAME}/{SAMPLE_FILE_FILE_PATH}")
    s3_fs_client.remove_file(f"s3://{BUCKET_NAME}/{SAMPLE_FILE_FILE_PATH}")
    assert not s3_fs_client.exists(
        f"s3://{BUCKET_NAME}/{SAMPLE_FILE_FILE_PATH}"
    )

    #  local
    assert s3_fs_client.exists(SAMPLE_FILE_FILE_PATH)
    s3_fs_client.remove_file(SAMPLE_FILE_FILE_PATH)
    assert not s3_fs_client.exists(SAMPLE_FILE_FILE_PATH)


def test_copy_directory_both_ways_works(s3_fs_client: s3_fs, mock_s3) -> None:
    # from local to s3
    assert not s3_fs_client.exists(f"s3://{BUCKET_NAME}/{SAMPLE_FOLDER}")

    s3_fs_client.copy_directory(
        SAMPLE_FOLDER, f"s3://{BUCKET_NAME}/{SAMPLE_FOLDER}"
    )
    assert s3_fs_client.exists(f"s3://{BUCKET_NAME}/{SAMPLE_FOLDER}")

    assert len(
        s3_fs_client.list_directory(f"s3://{BUCKET_NAME}/{SAMPLE_FOLDER}")
    ) == len(s3_fs_client.list_directory(SAMPLE_FOLDER))

    # from s3 to local
    assert not s3_fs_client.exists(f"{DOWNLOADS}/{SAMPLE_FOLDER}")

    s3_fs_client.copy_directory(
        f"s3://{BUCKET_NAME}/{SAMPLE_FOLDER}", f"{DOWNLOADS}/{SAMPLE_FOLDER}"
    )
    assert s3_fs_client.exists(f"{DOWNLOADS}/{SAMPLE_FOLDER}")

    assert len(
        s3_fs_client.list_directory(f"/{DOWNLOADS}/{SAMPLE_FOLDER}")
    ) == len(s3_fs_client.list_directory(SAMPLE_FOLDER))


def test_remove_directory(
    s3_fs_client: s3_fs,
    mock_s3_with_sample_file,
) -> None:
    # s3
    assert s3_fs_client.exists(f"s3://{BUCKET_NAME}/{SAMPLE_FOLDER}")
    s3_fs_client.remove_directory(f"s3://{BUCKET_NAME}/{SAMPLE_FOLDER}")
    assert not s3_fs_client.exists(f"s3://{BUCKET_NAME}/{SAMPLE_FOLDER}")

    #  local
    assert s3_fs_client.exists(SAMPLE_FOLDER)
    s3_fs_client.remove_directory(SAMPLE_FOLDER)
    assert not s3_fs_client.exists(SAMPLE_FOLDER)


def test_create_file_if_not_exists(s3_fs_client: s3_fs, mock_s3) -> None:
    s3_fs_client.create_file_if_not_exists(f"s3://{BUCKET_NAME}/new-file.txt")
    assert s3_fs_client.exists(f"s3://{BUCKET_NAME}/new-file.txt")


def test_create_directory(s3_fs_client: s3_fs, mock_s3) -> None:
    s3_fs_client.create_directory(f"s3://{BUCKET_NAME}/new-folder")
    assert s3_fs_client.exists(f"s3://{BUCKET_NAME}/new-folder")


def test_user(s3_fs_client: s3_fs) -> None:
    assert s3_fs_client.user == "1234"


def test_init_from_env_vars() -> None:
    with env.env_vars_set(
        {
            s3_fs._USERNAME_ENV_VAR: "env-username",
            s3_fs._PASSWORD_ENV_VAR: "env-password",
        }
    ):
        client = s3_fs.S3FileService.from_env()
        assert client.aws_access_key_id == "env-username"
        assert client.aws_secret_access_key == "env-password"


def test_init_from_connection_id(
    mock_api_creds_retrieval,
    fake_connection,
    fake_connection_id,
) -> None:
    with env.env_vars_set({"MANTIK_USERNAME": "X", "MANTIK_PASSWORD": "X"}):
        client = s3_fs.S3FileService.from_env(connection_id=fake_connection_id)
        assert client.aws_access_key_id == fake_connection.login_name
        assert client.aws_secret_access_key == fake_connection.password
