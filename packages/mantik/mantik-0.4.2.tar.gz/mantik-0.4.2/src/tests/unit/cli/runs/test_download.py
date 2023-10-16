import click.testing

import mantik.cli.main as main
import mantik.utils.env as env


def test_get_logs_with_api_url(fake_client, mantik_env_variables):
    with env.env_vars_set(mantik_env_variables):
        runner = click.testing.CliRunner()
        result = runner.invoke(
            main.cli,
            [
                "runs",
                "download",
                *[
                    "--api-url=https://test-uri.com",
                    "--remote-path=stdout",
                    "--local-path=~",
                    "test_job_url5",
                ],
            ],
        )

        assert result.exit_code == 0


def test_get_logs_with_api_url_of_non_existent_file(
    fake_client, mantik_env_variables
):
    with env.env_vars_set(mantik_env_variables):
        runner = click.testing.CliRunner()
        result = runner.invoke(
            main.cli,
            [
                "runs",
                "download",
                *[
                    "--api-url=https://test-uri.com",
                    "--remote-path=file_does_not_exist",
                    "--local-path=~",
                    "test_job_url5",
                ],
            ],
        )

        assert result.exit_code == 1
        assert isinstance(result.exception, FileNotFoundError)


def test_get_logs_with_config_and_fake_dir(
    fake_client, example_project_path, mantik_env_variables, tmpdir
):
    output_dir = tmpdir / "this/path/does/not/exist"
    with env.env_vars_set(mantik_env_variables):
        runner = click.testing.CliRunner()
        result = runner.invoke(
            main.cli,
            [
                "runs",
                "download",
                *[
                    f"--backend-config={example_project_path}/compute-backend-config.json",  # noqa
                    "--remote-path=fake_dir",
                    f"--local-path={output_dir}",
                    "test_job_url7",
                ],
            ],
        )

        assert result.exit_code == 0


def test_download_all(
    fake_client, example_project_path, mantik_env_variables, tmpdir
):
    output_dir = tmpdir / "this/path/does/not/exist"
    with env.env_vars_set(mantik_env_variables):
        runner = click.testing.CliRunner()
        result = runner.invoke(
            main.cli,
            [
                "runs",
                "download",
                *[
                    f"--backend-config={example_project_path}/compute-backend-config.json",  # noqa
                    f"--local-path={output_dir}",
                    "test_job_url7",
                ],
            ],
        )

        assert result.exit_code == 0


def test_get_logs_with_no_option(mantik_env_variables):
    with env.env_vars_set(mantik_env_variables):
        runner = click.testing.CliRunner()
        result = runner.invoke(
            main.cli,
            [
                "runs",
                "download",
                *[
                    "test-id1",
                    "--remote-path=fake_dir",
                    "--local-path=/path/to/file",
                ],
            ],
        )

        assert result.exit_code == 1
        assert isinstance(result.exception, ValueError)
