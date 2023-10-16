import click.testing

import mantik.cli.main as main
import mantik.utils as utils


def test_mutual_exclusive(
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
                    "--api-url=https://test-uri.com",
                    f"--backend-config={example_project_path}/compute-backend-config.json",  # noqa
                    "test_job_url5",
                ],
            ],
        )

        assert result.exit_code == 2
        assert (
            result.output == "Error: Illegal usage: `backend_config` "
            "is mutually exclusive with `api_url`\n"
        )
