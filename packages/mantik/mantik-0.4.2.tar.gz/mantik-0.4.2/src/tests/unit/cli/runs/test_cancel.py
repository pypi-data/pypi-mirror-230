import click.testing

import mantik.cli.main as main
import mantik.utils as utils


def test_cancel_jobs(fake_client, mantik_env_variables):
    with utils.env.env_vars_set(mantik_env_variables):
        runner = click.testing.CliRunner()
        result = runner.invoke(
            main.cli,
            [
                "runs",
                "cancel",
                *["--api-url=https://test-uri.com", "test_job_url5"],
            ],
        )

        assert result.exit_code == 0
        assert result.output == "Cancelled job test_job_url5.\n"
