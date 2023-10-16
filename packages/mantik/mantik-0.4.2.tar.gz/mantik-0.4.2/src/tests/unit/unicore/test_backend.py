import functools
import json
import pathlib

import mlflow.projects as projects
import pyunicore.client

import mantik.testing as testing
import mantik.unicore.backend as backend
import mantik.unicore.client as client_wrapper
import mantik.unicore.config.core as core
import mantik.unicore.credentials as unicore_credentials
import mantik.utils as utils

FILE_PATH = pathlib.Path(__file__).parent

ALL_ENV_VARS = [
    unicore_credentials._USERNAME_ENV_VAR,
    unicore_credentials._PASSWORD_ENV_VAR,
    core._PROJECT_ENV_VAR,
]


class FakeProject:
    pass


class TestUnicoreBackend:
    def test_run(
        self, monkeypatch, example_project_path, tmpdir, env_vars_set, caplog
    ):
        monkeypatch.setattr(
            pyunicore.client,
            "Transport",
            testing.pyunicore.FakeTransport,
        )
        fake_client_with_successful_login = functools.partial(
            testing.pyunicore.FakeClient,
            login_successful=True,
        )
        monkeypatch.setattr(
            pyunicore.client,
            "Client",
            fake_client_with_successful_login,
        )
        backend_config_path = (
            example_project_path / "compute-backend-config.json"
        )
        with open(backend_config_path) as infile:
            backend_config = json.load(infile)
        # Following env vars are set by MLflow before running a project.
        backend_config[
            projects.PROJECT_STORAGE_DIR
        ] = example_project_path.as_posix()

        # Point MLFLOW_TRACKING_URI to a temporary directory
        tracking_uri = tmpdir / "mlruns"

        run_name = "my incredible run"

        with env_vars_set(
            {
                # Following env vars must be set for the config.
                **{key: "test-val" for key in ALL_ENV_VARS},
                utils.mlflow.TRACKING_URI_ENV_VAR: f"file://{tracking_uri}",
                utils.mlflow.RUN_NAME_ENV_VAR: run_name,
            }
        ):
            submitted_run = backend.UnicoreBackend().run(
                project_uri=example_project_path.as_posix(),
                entry_point="main",
                params={"print": "test"},
                version=None,
                backend_config=backend_config,
                tracking_uri=None,
                experiment_id=None,
            )

            assert submitted_run._job._job.started
            assert "with name my incredible run" in caplog.text


def test_submit_job_in_staging_in_and_upload_input_files(
    example_project_path, example_project, example_config
):
    client = testing.pyunicore.FakeClient()
    entry_point = example_project.get_entry_point("main")
    parameters = {"print": "test"}
    apptainer_image = example_project_path / "mantik-test.sif"
    client = client_wrapper.Client(client)
    backend._submit_job_in_staging_in_and_upload_input_files(
        client=client,
        entry_point=entry_point,
        parameters=parameters,
        storage_dir="",
        input_files=[apptainer_image],
        config=example_config,
        run_id="example_run_id",
    )


def test_create_job_description_apptainer(
    example_project_path, example_project, example_config
):
    entry_point = example_project.get_entry_point("main")
    parameters = {"print": "whatever"}
    storage_dir = "test-dir"
    expected = {
        "Executable": "srun apptainer",
        "Arguments": [
            "run",
            "--cleanenv",
            "--env MLFLOW_TRACKING_URI=${MLFLOW_TRACKING_URI:-file://$PWD/mlruns}",  # noqa: E501
            "${MLFLOW_TRACKING_TOKEN:+--env MLFLOW_TRACKING_TOKEN=$MLFLOW_TRACKING_TOKEN}",  # noqa: E501
            "${MLFLOW_EXPERIMENT_NAME:+--env MLFLOW_EXPERIMENT_NAME=$MLFLOW_EXPERIMENT_NAME}",  # noqa: E501
            "${MLFLOW_EXPERIMENT_ID:+--env MLFLOW_EXPERIMENT_ID=$MLFLOW_EXPERIMENT_ID}",  # noqa: E501
            "mantik-test.sif",
            "python",
            "main.py",
            "whatever",
        ],
        "Project": "test-project",
        "Resources": {"Queue": "batch"},
        "RunUserPrecommandOnLoginNode": False,
        "RunUserPostcommandOnLoginNode": False,
        "Stderr": "mantik.log",
        "Stdout": "mantik.log",
    }
    result = backend.create_job_description(
        entry_point=entry_point,
        parameters=parameters,
        storage_dir=storage_dir,
        config=example_config,
    )

    # Environment contains additional MLFLOW env vars,
    # which depend on the execution environment
    expected_environment = {"SRUN_CPUS_PER_TASK": 100}
    actual_environment = result.pop("Environment")
    assert all(
        actual_environment[key] == value
        for key, value in expected_environment.items()
    )

    assert result == expected


def test_create_job_description_python(
    example_project_path, example_project, example_config_for_python
):
    entry_point = example_project.get_entry_point("main")
    parameters = {"print": "whatever"}
    storage_dir = "test-dir"
    expected = {
        "Executable": "python",
        "Arguments": ["main.py", "whatever"],
        "User precommand": "source /venv/bin/activate",
        "Project": "test-project",
        "Resources": {"Queue": "batch"},
        "RunUserPrecommandOnLoginNode": False,
        "RunUserPostcommandOnLoginNode": False,
        "Stderr": "mantik.log",
        "Stdout": "mantik.log",
    }
    result = backend.create_job_description(
        entry_point=entry_point,
        parameters=parameters,
        storage_dir=storage_dir,
        config=example_config_for_python,
    )

    # Removing Environment for assertion since it contains additional MLFLOW
    # env vars, which depend on the execution environment
    result.pop("Environment", None)

    assert result == expected
