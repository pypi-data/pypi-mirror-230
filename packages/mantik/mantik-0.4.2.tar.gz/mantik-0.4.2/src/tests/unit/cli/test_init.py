import click.testing
import pytest

import mantik
import mantik.cli.main as main
import mantik.testing.token as testing_token


@pytest.mark.parametrize(
    ("cli_args", "expected"),
    [
        ([], "export MLFLOW_TRACKING_TOKEN=test-access-token\n"),
        (["--no-export"], "MLFLOW_TRACKING_TOKEN=test-access-token\n"),
    ],
)
@testing_token.set_token()
def test_init_from_env_vars(tmp_dir_as_test_mantik_folder, cli_args, expected):
    runner = click.testing.CliRunner()
    result = runner.invoke(main.cli, ["init", *cli_args])

    assert result.exit_code == 0
    assert result.output == expected
    mantik.testing.env.assert_conflicting_mlflow_env_vars_not_set()
    mantik.testing.env.assert_correct_tracking_token_env_var_set(
        "test-access-token"
    )
