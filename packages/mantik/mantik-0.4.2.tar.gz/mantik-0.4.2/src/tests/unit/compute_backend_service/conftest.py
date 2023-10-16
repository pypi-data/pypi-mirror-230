import json
import pathlib

import fastapi.testclient
import pytest

import mantik.compute_backend_service as compute_backend_service
import mantik.compute_backend_service.settings as settings
import mantik.mlflow_server.tokens.verifier as _verifier
import mantik.testing as testing
import mantik.unicore.config as _config
import mantik.unicore.config.core as core
import mantik.unicore.config.environment as environment
import mantik.unicore.config.executable as executable
import mantik.unicore.config.resources as resources
import mantik.unicore.utils.zip as unicore_zip


@pytest.fixture(scope="function")
def client(monkeypatch) -> fastapi.testclient.TestClient:
    monkeypatch.setattr(
        _verifier,
        "TokenVerifier",
        testing.mlflow_server.FakeTokenVerifier,
    )
    app = compute_backend_service.app.create_app(global_path_prefix="")

    return fastapi.testclient.TestClient(app, raise_server_exceptions=False)


@pytest.fixture(scope="function")
def client_with_small_size_limitation(
    monkeypatch,
) -> fastapi.testclient.TestClient:
    monkeypatch.setattr(
        _verifier,
        "TokenVerifier",
        testing.mlflow_server.FakeTokenVerifier,
    )
    app = compute_backend_service.app.create_app(global_path_prefix="")

    def get_settings_override() -> settings.Settings:
        return settings.Settings(max_file_size=1)

    app.dependency_overrides[settings.get_settings] = get_settings_override

    return fastapi.testclient.TestClient(app, raise_server_exceptions=False)


@pytest.fixture
def submit_run_request_data():
    return {
        "run_name": "test-run-name",
        "entry_point": "main",
        "mlflow_parameters": json.dumps({"foo": "bar"}),
        "unicore_user": "bar",
        "compute_budget_account": "baz",
        "unicore_password": "bam",
        "compute_backend_config": "compute-backend-config.json",
        "experiment_id": "1",
        "mlflow_tracking_uri": "foo",
        "mlflow_tracking_token": "aasdf",
    }


@pytest.fixture(scope="session")
def mlproject_path() -> pathlib.Path:
    return (
        pathlib.Path(__file__).parent
        / "../../../../src/tests/resources/test-project"
    )


@pytest.fixture(scope="function")
def example_config() -> core.Config:
    return core.Config(
        api_url="test-url",
        user="user",
        password="password",
        project="test-project",
        environment=environment.Environment(
            execution=executable.Apptainer(
                path=pathlib.Path("mantik-test.sif"),
            )
        ),
        resources=resources.Resources(queue="batch"),
        exclude=[],
    )


@pytest.fixture()
def zipped_content(mlproject_path, example_config):
    return unicore_zip.zip_directory_with_exclusion(
        mlproject_path, example_config
    )


@pytest.fixture()
def submit_run_request_files(zipped_content):
    return {"mlproject_zip": zipped_content}


@pytest.fixture(scope="session")
def broken_mlproject_path() -> pathlib.Path:
    return (
        pathlib.Path(__file__).parent
        / "../../../../src/tests/resources/broken-project"
    )


@pytest.fixture(scope="function")
def broken_config() -> _config.core.Config:
    return _config.core.Config(
        api_url="test-url",
        user="user",
        password="password",
        project="test-project",
        environment=_config.environment.Environment(
            execution=_config.executable.Apptainer(
                path=pathlib.Path("/mantik-test.sif"), type="remote"
            )
        ),
        resources=_config.resources.Resources(queue="batch"),
        exclude=[],
    )


@pytest.fixture()
def broken_zipped_content(broken_mlproject_path, broken_config):
    return unicore_zip.zip_directory_with_exclusion(
        broken_mlproject_path, broken_config
    )
