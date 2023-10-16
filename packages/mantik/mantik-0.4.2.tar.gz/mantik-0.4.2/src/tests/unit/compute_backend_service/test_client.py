import dataclasses

import pytest

import mantik.compute_backend_service.client as _client
import mantik.compute_backend_service.models as _models
import mantik.testing.token as testing_token
import mantik.unicore.config.core as core
import mantik.unicore.credentials as unicore_credentials
import mantik.utils as utils

TEST_MLFLOW_TRACKING_URI = "https://tracking.test-uri.com"
ENV_VARS = {
    unicore_credentials._USERNAME_ENV_VAR: "test-user",
    unicore_credentials._PASSWORD_ENV_VAR: "test-password",
    core._PROJECT_ENV_VAR: "test-project",
    utils.mlflow.TRACKING_URI_ENV_VAR: TEST_MLFLOW_TRACKING_URI,
}


@dataclasses.dataclass
class FakeSubmittedRun:
    run_id: int = 0
    job_id: int = 0


@pytest.fixture(autouse=True)
def set_required_env_vars(required_env_vars):
    with utils.env.env_vars_set({**required_env_vars, **ENV_VARS}):
        yield


@pytest.fixture()
@testing_token.set_token()
def compute_backend_client(
    set_required_env_vars,
) -> _client.ComputeBackendClient:
    return _client.ComputeBackendClient.from_env()


class TestComputeBackendClient:
    def test_url(self, compute_backend_client):
        expected = "https://computebackend.test-uri.com/compute-backend"

        result = compute_backend_client.url

        assert result == expected

    def test_submit_url(self, compute_backend_client):
        expected = "https://computebackend.test-uri.com/compute-backend/submit"

        result = compute_backend_client.submit_url

        assert result == expected

    def test_submit(
        self,
        requests_mock,
        compute_backend_client,
        tmp_dir_as_test_mantik_folder,
        mlproject_path,
    ):
        experiment_id = 123
        run_id = 0
        unicore_job_id = 1

        expected = _models.SubmitRunResponse(
            experiment_id=experiment_id,
            run_id=run_id,
            unicore_job_id=unicore_job_id,
        )

        # Note: fastapi converts pydantic.BaseModel to dict
        # https://github.com/tiangolo/fastapi/blob/master/fastapi/routing.py#L77
        requests_mock.post(
            f"{compute_backend_client.submit_url}/{experiment_id}",
            json=expected.dict(),
            status_code=201,
        )

        result = compute_backend_client.submit_run(
            run_name="test-run-name",
            experiment_id=experiment_id,
            mlproject_path=mlproject_path,
            mlflow_parameters={"test-parameter": "test-value"},
            backend_config="compute-backend-config.json",
            entry_point="main",
        )

        assert result.status_code == 201
        assert result.json() == expected.dict()
