import logging
import unittest.mock

import click.testing
import pytest

import mantik.cli.main as main
import mantik.cli.remote_file_service.unicore_file_service as cli_uc_fs
import mantik.testing.remote_file_service as testing

GROUP_NAME = cli_uc_fs.GROUP_NAME


@pytest.fixture
def fake_data_client():
    with unittest.mock.patch(
        "mantik.remote_file_service.data_client.DataClient.from_env",
        return_value=testing.FakeUnicoreFileService(),
    ) as mock:
        yield mock


@pytest.fixture
def fake_unicore_file_service(fake_data_client):
    with unittest.mock.patch(
        "mantik.remote_file_service.unicore_file_service.UnicoreFileService.from_env",  # noqa
        return_value=testing.FakeUnicoreFileService(),
    ) as mock:
        yield mock


@pytest.fixture
def cli_test_runner():
    yield click.testing.CliRunner()


@pytest.fixture
def debug_caplog(caplog):
    caplog.set_level(logging.DEBUG)
    yield caplog


def test_copy_file(fake_unicore_file_service, debug_caplog, cli_test_runner):
    result = cli_test_runner.invoke(
        main.cli,
        [
            GROUP_NAME,
            "copy-file",
            "/fake-dir/fake.file",
            "remote:/fake-dir/fake.file",
        ],
    )

    assert result.exit_code == 0
    assert result.output == str(testing.fake_file) + "\n"
    assert (
        "copy_file /fake-dir/fake.file remote:/fake-dir/fake.file"
        in debug_caplog.text
    )


def test_remove_file(fake_unicore_file_service, debug_caplog, cli_test_runner):
    result = cli_test_runner.invoke(
        main.cli,
        [
            GROUP_NAME,
            "remove-file",
            "remote:/fake-dir/fake.file",
        ],
    )

    assert result.exit_code == 0
    assert "remove_file remote:/fake-dir/fake.file" in debug_caplog.text


def test_create_file_if_not_exists(
    fake_unicore_file_service, debug_caplog, cli_test_runner
):
    result = cli_test_runner.invoke(
        main.cli,
        [
            GROUP_NAME,
            "create-file",
            "remote:/fake-dir/fake.file",
        ],
    )

    assert result.exit_code == 0
    assert result.output == str(testing.fake_file) + "\n"
    assert (
        "create_file_if_not_exists remote:/fake-dir/fake.file"
        in debug_caplog.text
    )


def test_list_directory(
    fake_unicore_file_service, debug_caplog, cli_test_runner
):
    result = cli_test_runner.invoke(
        main.cli,
        [
            GROUP_NAME,
            "list-directory",
            "remote:/fake-dir/fake.file",
        ],
    )

    assert result.exit_code == 0
    assert result.output == str(testing.fake_directory.children) + "\n"
    assert "list_directory remote:/fake-dir/fake.file" in debug_caplog.text


def test_create_directory(
    fake_unicore_file_service, debug_caplog, cli_test_runner
):
    result = cli_test_runner.invoke(
        main.cli,
        [
            GROUP_NAME,
            "create-directory",
            "remote:/fake-dir",
        ],
    )

    assert result.exit_code == 0
    assert result.output == str(testing.fake_directory) + "\n"
    assert "create_directory remote:/fake-dir" in debug_caplog.text


def test_remove_directory(
    fake_unicore_file_service, debug_caplog, cli_test_runner
):
    result = cli_test_runner.invoke(
        main.cli,
        [
            GROUP_NAME,
            "remove-directory",
            "remote:/fake-dir",
        ],
    )

    assert result.exit_code == 0
    assert "remove_directory remote:/fake-dir" in debug_caplog.text


def test_directory_file(
    fake_unicore_file_service, debug_caplog, cli_test_runner
):
    result = cli_test_runner.invoke(
        main.cli,
        [
            GROUP_NAME,
            "copy-directory",
            "/fake-dir",
            "remote:/fake-dir",
        ],
    )

    assert result.exit_code == 0
    assert result.output == str(testing.fake_directory) + "\n"
    assert "copy_directory /fake-dir remote:/fake-dir" in debug_caplog.text


def test_exists(fake_unicore_file_service, debug_caplog, cli_test_runner):
    result = cli_test_runner.invoke(
        main.cli,
        [
            GROUP_NAME,
            "exists",
            "remote:/fake-dir/fake.file",
        ],
    )

    assert result.exit_code == 0
    assert result.output == "True\n"


def test_user(fake_unicore_file_service, debug_caplog, cli_test_runner):
    result = cli_test_runner.invoke(
        main.cli,
        [
            GROUP_NAME,
            "user",
        ],
    )

    assert result.exit_code == 0
    assert result.output == "FAKE-USER\n"


def test_cli_operation_with_wrong_connection_id(
    fake_unicore_file_service, debug_caplog, cli_test_runner
):
    result = cli_test_runner.invoke(
        main.cli,
        [
            GROUP_NAME,
            "copy-file",
            "/fake-dir/fake.file",
            "remote:/fake-dir/fake.file",
            "--connection-id",
            "wrong-id-type",
        ],
    )
    assert "Error: Invalid value for '--connection-id'" in result.output
    assert result.exit_code == 2
