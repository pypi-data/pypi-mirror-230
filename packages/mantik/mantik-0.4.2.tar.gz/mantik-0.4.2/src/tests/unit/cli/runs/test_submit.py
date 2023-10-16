import argparse

import click.testing
import pytest

import mantik.cli.main as main
import mantik.cli.runs.submit as submit
import mantik.compute_backend_service.api as api
import mantik.compute_backend_service.client as _client
import mantik.testing.token as testing_token
import mantik.unicore.config.core as core
import mantik.unicore.credentials as unicore_credentials
import mantik.utils as utils
import mantik.utils.mantik_api.credentials as _credentials

TEST_MLFLOW_TRACKING_URI = "https://tracking.test-uri.com"
TEST_COMPUTE_BACKEND_URL = (
    f"https://{_client._DEFAULT_COMPUTE_BACKEND_SUBDOMAIN}.test-uri.com"
    f"{_client._DEFAULT_COMPUTE_BACKEND_API_PATH}"
)

ENV_VARS = {
    unicore_credentials._USERNAME_ENV_VAR: "test-user",
    unicore_credentials._PASSWORD_ENV_VAR: "test-password",
    core._PROJECT_ENV_VAR: "test-project",
    utils.mlflow.TRACKING_URI_ENV_VAR: TEST_MLFLOW_TRACKING_URI,
    utils.mlflow.EXPERIMENT_ID_ENV_VAR: "0",
    _credentials._MANTIK_USERNAME_ENV_VAR: "mantik-user",
    _credentials._MANTIK_PASSWORD_ENV_VAR: "matik_password",
}

SUCCESS_JSON_RESPONSE = {
    "experiment_id": "test-experiment-id",
    "run_id": "test-run-id",
    "unicore_job_id": "test-unicore-job-id",
}


@pytest.mark.parametrize(
    ("cli_args", "expected"),
    [
        (
            [
                "--run-name=test-run",
                "--backend-config=compute-backend-config.json",
            ],
            0,
        ),
        (
            [
                "--run-name=test-run",
                "--backend-config=compute-backend-config.json",
                "-P a=99",
                "-P b=hello",
            ],
            0,
        ),
        ([], 2),
    ],
)
@testing_token.set_token()
def test_run_project(cli_args, expected, requests_mock, example_project_path):
    cli_args.append(example_project_path)
    with utils.env.env_vars_set(ENV_VARS):
        requests_mock.post(
            f"{TEST_COMPUTE_BACKEND_URL}"
            f"{api.SUBMIT_PATH}/{ENV_VARS['MLFLOW_EXPERIMENT_ID']}",
            json=SUCCESS_JSON_RESPONSE,
            status_code=201,
        )

        runner = click.testing.CliRunner()
        result = runner.invoke(main.cli, ["runs", "submit", *cli_args])

        assert result.exit_code == expected


@testing_token.set_token()
def test_run_project_with_absolute_path_for_backend_config(
    requests_mock, example_project_path
):
    cli_args = [
        example_project_path,
        f"--backend-config={example_project_path}/compute-backend-config.json",
        "--run-name=test-run",
    ]
    with utils.env.env_vars_set(ENV_VARS):
        requests_mock.post(
            f"{TEST_COMPUTE_BACKEND_URL}"
            f"{api.SUBMIT_PATH}/{ENV_VARS['MLFLOW_EXPERIMENT_ID']}",
            status_code=201,
            json=SUCCESS_JSON_RESPONSE,
        )

        runner = click.testing.CliRunner()
        result = runner.invoke(main.cli, ["runs", "submit", *cli_args])

        assert result.exit_code == 0


@testing_token.set_token()
def test_run_project_with_connection_id(
    example_project_path, mock_mantik_api_request, mock_token_sub, user_id
):
    connection_id = "46a552bf-85df-4205-bda4-9515bd3e19a1"
    cli_args = [
        example_project_path,
        "--backend-config=compute-backend-config.json",
        f"--connection-id={connection_id}",
        "--run-name=test-run",
    ]
    with utils.env.env_vars_set(ENV_VARS), mock_mantik_api_request(
        method="GET",
        end_point=f"/mantik-api/users/{user_id}/settings/connections/{connection_id}",  # noqa
        status_code=200,
        json_response={
            "connectionId": connection_id,
            "user": {
                "userId": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "name": "test-name",
                "email": "email-test",
            },
            "connectionName": "connection",
            "connectionProvider": "string",
            "authMethod": "string",
            "loginName": "test-user",
            "password": "12345test",
            "token": "string",
        },
    ) as (
        m,
        error,
    ):
        m.register_uri(
            method="POST",
            url=f"{TEST_COMPUTE_BACKEND_URL}"
            f"{api.SUBMIT_PATH}/{ENV_VARS['MLFLOW_EXPERIMENT_ID']}",
            status_code=201,
            json=SUCCESS_JSON_RESPONSE,
        )

        runner = click.testing.CliRunner()
        result = runner.invoke(main.cli, ["runs", "submit", *cli_args])

        assert result.exit_code == 0


@testing_token.set_token()
def test_run_project_with_set_log_level(
    requests_mock, example_project_path, caplog
):
    with utils.env.env_vars_set(ENV_VARS):
        requests_mock.post(
            f"{TEST_COMPUTE_BACKEND_URL}"
            f"{api.SUBMIT_PATH}/{ENV_VARS['MLFLOW_EXPERIMENT_ID']}",
            json=SUCCESS_JSON_RESPONSE,
            status_code=201,
        )
        runner = click.testing.CliRunner()
        _ = runner.invoke(
            main.cli,
            [
                "runs",
                "submit",
                example_project_path,
                f"--backend-config={example_project_path}/compute-backend-config.json",  # noqa: E501
                "--verbose",
                "--run-name=test-run",
            ],
        )
        assert any("DEBUG" in m for m in caplog.messages)


@pytest.mark.parametrize(
    ("string_list", "expected_dict"),
    [
        (
            [
                "n_components=3",
                "n_components2=2.7",
                "data='/opt/data/temperature_level_128'",
                "url==========",
            ],
            {
                "n_components": 3,
                "n_components2": 2.7,
                "data": "/opt/data/temperature_level_128",
                "url": "=========",
            },
        ),
    ],
)
def test_dict_from_list(string_list, expected_dict):
    assert expected_dict == submit._dict_from_list(string_list)


@pytest.mark.parametrize(
    ("parameter_sting", "expected"),
    [
        ("n_components=3", ("n_components", 3)),
        ("n_components=2.7", ("n_components", 2.7)),
        (
            "data='/opt/data/temperature_level_128_daily_averages_2020.nc'",
            ("data", "/opt/data/temperature_level_128_daily_averages_2020.nc"),
        ),
        (
            'data="/opt/data/temperature_level_128_daily_averages_2020.nc"',
            ("data", "/opt/data/temperature_level_128_daily_averages_2020.nc"),
        ),
        (
            "data=/opt/data/temperature_level_128_daily_averages_2020.nc",
            ("data", "/opt/data/temperature_level_128_daily_averages_2020.nc"),
        ),
        ("url==========", ("url", "=========")),
    ],
)
def test_parse_parameter_from_string(parameter_sting, expected):
    assert expected == submit._parse_parameter_from_string(parameter_sting)


@pytest.mark.parametrize(
    ("string", "expected"),
    [
        ("3", 3),
        ("2.7", 2.7),
        (
            "/opt/data/temperature_level_128_daily_averages_2020.nc",
            "/opt/data/temperature_level_128_daily_averages_2020.nc",
        ),
    ],
)
def test_parse_value(string, expected):
    assert expected == submit._parse_value(string)


def test_parse_value_try_injection():
    injection = "_parse_parameter_from_string('a=2')"
    with pytest.raises(argparse.ArgumentTypeError) as parse_error:
        submit._parse_value(injection)
    assert f"Unable to parse {injection}" in str(parse_error.value)
