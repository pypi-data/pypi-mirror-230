import dataclasses
import json
import unittest.mock

import pytest
import starlette.status

import mantik.compute_backend_service.api as api
import mantik.compute_backend_service.models


@dataclasses.dataclass
class FakeSubmittedRun:
    run_id: int = 0
    job_id: int = 1


@pytest.mark.parametrize(
    ("headers", "expected"),
    [
        ({}, 401),
        (
            {"Authorization": "test-invalid-token"},
            401,
        ),
        (
            {"Authorization": "Bearer test-invalid-token"},
            401,
        ),
        (
            {"Authorization": "Bearer test-valid-token"},
            201,
        ),
    ],
)
@unittest.mock.patch(
    "mlflow.projects.run",
    return_value=FakeSubmittedRun(),
)
def test_submit_run(mock_mlflow_run, client, zipped_content, headers, expected):
    response = client.post(
        f"{api.SUBMIT_PATH}/0",
        data={
            "run_name": "test-name",
            "entry_point": "main",
            "mlflow_parameters": json.dumps({"foo": "bar"}),
            "unicore_user": "bar",
            "unicore_password": "baz",
            "compute_budget_account": "empty",
            "mlflow_tracking_uri": "foo.bar",
            "mlflow_tracking_token": "abcdefghijk",
        },
        files={"mlproject_zip": zipped_content.read()},
        headers=headers,
    )

    assert response.status_code == expected

    if expected == 201:
        assert response.json() == {
            "experiment_id": 0,
            "run_id": "0",
            "unicore_job_id": "1",
        }
        mock_mlflow_run.assert_called()


@unittest.mock.patch(
    "mlflow.projects.run",
    return_value=FakeSubmittedRun(),
)
def test_submit_run_invalid_backend_config_type(
    mock_mlflow_run, client, zipped_content
):
    unsupported_format = ".yamml"
    response = client.post(
        f"{api.SUBMIT_PATH}/0",
        data={
            "run_name": "test-name",
            "entry_point": "main",
            "mlflow_parameters": json.dumps({"foo": "bar"}),
            "unicore_user": "bar",
            "unicore_password": "baz",
            "compute_budget_account": "empty",
            "mlflow_tracking_uri": "foo.bar",
            "mlflow_tracking_token": "abcdefghijk",
            "compute_backend_config": f"compute-backend-config{unsupported_format}",  # noqa: E501
        },
        files={"mlproject_zip": zipped_content.read()},
        headers={"Authorization": "Bearer test-valid-token"},
    )

    error_message = response.json()["message"]
    mock_mlflow_run.assert_not_called()
    assert response.status_code == 400
    assert (
        error_message == "While submitting the job, "
        "this configuration error occurred: "
        f"The given file type '{unsupported_format}'"
        " is not supported for the config,"
        " the supported ones are: '.json', '.yml', '.yaml'."
    )


@unittest.mock.patch(
    "mantik.compute_backend_service.backend.handle_submit_run_request",
    return_value=mantik.compute_backend_service.models.SubmitRunResponse(
        experiment_id=0, run_id=0, unicore_job_id=0
    ),
)
@unittest.mock.patch("tempfile.TemporaryFile")
def test_memory_freed_when_success(
    mock_temporary_file,
    mock_handle_submit_run_request,
    client,
    zipped_content,  # noqa
):
    response = client.post(
        f"{api.SUBMIT_PATH}/0",
        data={
            "run_name": "test-name",
            "entry_point": "main",
            "mlflow_parameters": json.dumps({"foo": "bar"}),
            "unicore_user": "bar",
            "unicore_password": "baz",
            "compute_budget_account": "empty",
            "mlflow_tracking_uri": "foo.bar",
            "mlflow_tracking_token": "abcdefghijk",
            "compute_backend_config": "backend-config.yaml",
        },
        files={"mlproject_zip": zipped_content.read()},
        headers={"Authorization": "Bearer test-valid-token"},
    )
    assert response.status_code == 201
    mock_temporary_file.assert_called()
    mock_temporary_file().write.assert_called()
    mock_temporary_file().seek.assert_called()
    mock_temporary_file().close.assert_called()
    mock_handle_submit_run_request.assert_called()


@unittest.mock.patch(
    "mantik.compute_backend_service.backend.handle_submit_run_request",
    **{"return_value.raiseError.side_effect": Exception},
)
@unittest.mock.patch("tempfile.TemporaryFile")
def test_memory_freed_when_exception(
    mock_temp_file, mocked_run, client, zipped_content
):
    mocked_run.side_effect = Exception
    response = client.post(
        f"{api.SUBMIT_PATH}/0",
        data={
            "run_name": "test-name",
            "entry_point": "main",
            "mlflow_parameters": json.dumps({"foo": "bar"}),
            "unicore_user": "bar",
            "unicore_password": "baz",
            "compute_budget_account": "empty",
            "mlflow_tracking_uri": "foo.bar",
            "mlflow_tracking_token": "abcdefghijk",
        },
        files={"mlproject_zip": zipped_content.read()},
        headers={"Authorization": "Bearer test-valid-token"},
    )

    assert response.status_code == 500
    mock_temp_file().close.assert_called()


def test_submit_too_large_file(
    client_with_small_size_limitation, zipped_content
):
    response = client_with_small_size_limitation.post(
        f"{api.SUBMIT_PATH}/0",
        data={
            "run_name": "test-name",
            "entry_point": "main",
            "mlflow_parameters": json.dumps({"foo": "bar"}),
            "unicore_user": "bar",
            "unicore_password": "baz",
            "compute_budget_account": "empty",
            "mlflow_tracking_uri": "foo.bar",
            "mlflow_tracking_token": "abcdefghijk",
        },
        files={"mlproject_zip": zipped_content},
        headers={"Authorization": "Bearer test-valid-token"},
    )
    assert (
        response.status_code
        == starlette.status.HTTP_413_REQUEST_ENTITY_TOO_LARGE
    )
