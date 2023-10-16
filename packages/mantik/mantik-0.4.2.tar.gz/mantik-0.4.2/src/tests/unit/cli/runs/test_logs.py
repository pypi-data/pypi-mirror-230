import click.testing

import mantik.cli.main as main
import mantik.utils as utils


def test_get_logs_with_api_url(fake_client, mantik_env_variables):
    with utils.env.env_vars_set(mantik_env_variables):
        runner = click.testing.CliRunner()
        result = runner.invoke(
            main.cli,
            [
                "runs",
                "logs",
                *["--api-url=https://test-uri.com", "test_job_url5"],
            ],
        )

        assert result.exit_code == 0
        assert result.output == "Stat mantik.log\n"


def test_get_logs_with_config(
    fake_client, example_project_path, mantik_env_variables
):
    with utils.env.env_vars_set(mantik_env_variables):
        runner = click.testing.CliRunner()
        result = runner.invoke(
            main.cli,
            [
                "runs",
                "logs",
                *[
                    f"--backend-config={example_project_path}/compute-backend-config.json",  # noqa
                    "test_job_url7",
                ],
            ],
        )

        assert result.exit_code == 0
        assert result.output == "Stat mantik.log\n"


def test_get_logs_with_no_option(mantik_env_variables):
    with utils.env.env_vars_set(mantik_env_variables):
        runner = click.testing.CliRunner()
        result = runner.invoke(
            main.cli,
            [
                "runs",
                "logs",
                *["test-id1"],
            ],
        )

        assert result.exit_code == 1
        assert isinstance(result.exception, ValueError)
