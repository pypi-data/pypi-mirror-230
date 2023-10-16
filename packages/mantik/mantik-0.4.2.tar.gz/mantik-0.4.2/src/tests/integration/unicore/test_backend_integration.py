"""Integration tests for UNICORE.

**WARNING:** The UNICORE container takes up to 15-30 seconds to process a job,
hence be careful with the number of test cases used.


"""
import pathlib

import mlflow.projects as projects
import pytest

import mantik.unicore.backend as backend
import mantik.unicore.config.core as core
import mantik.unicore.credentials as _unicore_credentials
import mantik.unicore.properties as properties
import mantik.utils as utils

FILE_PATH = pathlib.Path(__file__).parent


@pytest.fixture()
def required_unicore_env_vars(unicore_credentials) -> dict:
    return {
        _unicore_credentials._USERNAME_ENV_VAR: unicore_credentials["user"],
        _unicore_credentials._PASSWORD_ENV_VAR: unicore_credentials["password"],
        core._PROJECT_ENV_VAR: "test-project",
        utils.mlflow.RUN_NAME_ENV_VAR: "my run name",
    }


RESOUCES = {
    "Queue": "batch",
    "Runtime": "1h",
    "Nodes": 1,
    "TotalCPUs": 1,
    "CPUsPerNode": 1,
    "MemoryPerNode": "1M",
}

EXPECTED_RESOURCE_MESSAGES = (
    "Queue=batch",
    "Runtime=3600",
    "Nodes=1",
    "TotalCPUs=1",
    "CPUsPerNode=1",
    "MemoryPerNode=1048576",
    "Project=test-project",
)


class TestUnicoreBackend:
    @pytest.mark.parametrize(
        (
            "entry_point",
            "params",
            "backend_config",
            "expected_job_status",
            "expected_log_messages",
        ),
        [
            # Test case: Apptainer with 2 modules and 1 env var
            #
            # * Test case will fail since no Apptainer image present in
            #   UNICORE container
            (
                "main",
                {"print": "test"},
                {
                    "Environment": {
                        "Modules": ["Module1", "Module2"],
                        "Variables": {"TEST_VAR": "test_value"},
                        "Apptainer": {
                            "Path": "/does/not/exist.sif",
                            "Type": "remote",
                        },
                        "PreRunCommand": {
                            "Command": "echo precommand",
                            "ExecuteOnLoginNode": False,
                        },
                        "PostRunCommand": {
                            "Command": "echo postcommand",
                            "ExecuteOnLoginNode": False,
                        },
                    },
                    "Resources": RESOUCES,
                },
                properties.Status.FAILED,
                [
                    *EXPECTED_RESOURCE_MESSAGES,
                    "MLFLOW_RUN_ID=",
                    "; export MLFLOW_RUN_ID",
                    'TEST_VAR="test_value"; export TEST_VAR',
                    "echo precommand; module load Module1 Module2",
                    (
                        "srun apptainer run "
                        "--cleanenv "
                        "--env MLFLOW_TRACKING_URI=${MLFLOW_TRACKING_URI:-file://$PWD/mlruns} "  # noqa: E501
                        "${MLFLOW_TRACKING_TOKEN:+--env MLFLOW_TRACKING_TOKEN=$MLFLOW_TRACKING_TOKEN} "  # noqa: E501
                        "${MLFLOW_EXPERIMENT_NAME:+--env MLFLOW_EXPERIMENT_NAME=$MLFLOW_EXPERIMENT_NAME} "  # noqa: E501
                        "${MLFLOW_EXPERIMENT_ID:+--env MLFLOW_EXPERIMENT_ID=$MLFLOW_EXPERIMENT_ID} "  # noqa: E501
                        "/does/not/exist.sif "
                        "python main.py test"
                    ),
                    "echo postcommand",
                ],
            ),
            # Test case: Python with 2 modules and 1 env var
            #
            # * Test case will fail since no venv present in UNICORE container
            (
                "main",
                {"print": "test"},
                {
                    "Environment": {
                        "Modules": ["Module1", "Module2"],
                        "Variables": {"TEST_VAR": "test_value"},
                        "Python": {
                            "Path": "/does/not/exist",
                        },
                        "PreRunCommand": {
                            "Command": "echo precommand",
                            "ExecuteOnLoginNode": False,
                        },
                        "PostRunCommand": {
                            "Command": "echo postcommand",
                            "ExecuteOnLoginNode": False,
                        },
                    },
                    "Resources": RESOUCES,
                },
                properties.Status.FAILED,
                [
                    *EXPECTED_RESOURCE_MESSAGES,
                    "MLFLOW_RUN_ID=",
                    "; export MLFLOW_RUN_ID",
                    'TEST_VAR="test_value"; export TEST_VAR',
                    (
                        "echo precommand; "
                        "source /does/not/exist/bin/activate; "
                        "module load Module1 Module2"
                    ),
                    "python main.py test",
                    "echo postcommand",
                ],
            ),
            # Test case: No execution environment and echo entry point
            #
            # * Should succeed
            # * Pre/postcommand will be executed on login node, hence no modules
            #   loaded here. Modules would make the pre command fail (no modules
            #   in UNICORE container), and the main application will not be
            #   executed, as well as the post command.
            (
                "echo",
                {"output": "test"},
                {
                    "Environment": {
                        "Variables": {"TEST_VAR": "test_value"},
                        "PreRunCommand": {
                            "Command": "echo precommand",
                            "ExecuteOnLoginNode": True,
                        },
                        "PostRunCommand": {
                            "Command": "echo postcommand",
                            "ExecuteOnLoginNode": True,
                        },
                    },
                    "Resources": RESOUCES,
                },
                properties.Status.SUCCESSFUL,
                [
                    "Launched pre command <echo precommand>",
                    "Executing command: echo precommand",
                    "Execution on login node",
                    *EXPECTED_RESOURCE_MESSAGES,
                    'TEST_VAR="test_value"; export TEST_VAR',
                    "MLFLOW_RUN_ID=",
                    "; export MLFLOW_RUN_ID",
                    "echo test",
                    "Launched post command <echo postcommand>",
                    "Executing command: echo postcommand",
                    "Execution on login node",
                ],
            ),
        ],
    )
    def test_run(
        self,
        tmp_path,
        env_vars_set,
        unicore_api_url,
        required_unicore_env_vars,
        example_project_path,
        entry_point,
        params,
        backend_config,
        expected_job_status,
        expected_log_messages,
    ):
        backend_config = {
            **backend_config,
            "UnicoreApiUrl": unicore_api_url,
            # Following values are set by MLflow before running a project.
            projects.PROJECT_STORAGE_DIR: example_project_path.as_posix(),
        }

        expected_log_messages.extend(
            [
                # MLflow Tracking URI should be set by compute backend
                f'MLFLOW_TRACKING_URI="file://{tmp_path.as_posix()}/mlruns"; export MLFLOW_TRACKING_URI',  # noqa: E501
            ]
        )

        # Following env vars must be set for the config.
        tracking_uri = tmp_path / "mlruns"
        with env_vars_set(
            {
                **required_unicore_env_vars,
                # Point MLFLOW_TRACKING_URI to a temporary directory
                utils.mlflow.TRACKING_URI_ENV_VAR: f"file://{tracking_uri.as_posix()}",  # noqa: E501
            }
        ):
            result = backend.UnicoreBackend().run(
                project_uri=example_project_path.as_posix(),
                entry_point=entry_point,
                params=params,
                version=None,
                backend_config=backend_config,
                tracking_uri=None,
                experiment_id=None,
            )
            # Wait for job to fail or succeed
            result.wait()

        assert result._status == expected_job_status

        logs = "\n".join(result.logs)

        for message in expected_log_messages:
            assert message in logs, f"Message {message!r} not in logs"
