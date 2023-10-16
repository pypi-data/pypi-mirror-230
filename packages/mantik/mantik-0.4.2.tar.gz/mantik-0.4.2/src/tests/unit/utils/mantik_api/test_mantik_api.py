import uuid

import pytest
import requests

import mantik.utils.mantik_api.client as mantik_api
import mantik.utils.mlflow as mlflow


@pytest.mark.parametrize(
    ("status_code", "expected"), [(201, None), (404, requests.HTTPError())]
)
def test_create_data_repository(
    mock_mantik_api_request,
    add_data_repository,
    info_caplog,
    status_code,
    expected,
):
    project_id = uuid.uuid4()
    data_repository_id = uuid.uuid4()
    with mock_mantik_api_request(
        method="POST",
        end_point=f"/mantik-api/projects/{str(project_id)}/data",
        status_code=status_code,
        json_response={"dataRepositoryId": str(data_repository_id)},
        expected_error=expected,
    ) as (m, error):
        mantik_api.create_data_repository(
            add_data_repository=add_data_repository,
            project_id=project_id,
            token="test_token",
        )
        assert any(
            f"A new data repository with ID: {data_repository_id} "
            f"and name: {add_data_repository.data_repository_name} at "
            f"{add_data_repository.uri} has been created" in message
            for message in info_caplog.messages
        )
    if error:
        assert any(
            "Call to Mantik API" in message for message in info_caplog.messages
        )


@pytest.mark.parametrize(
    ("status_code", "expected"), [(204, None), (404, requests.HTTPError())]
)
def test_delete_data_repository(
    mock_mantik_api_request, info_caplog, status_code, expected
):
    project_id = uuid.uuid4()
    data_repository_id = uuid.uuid4()
    with mock_mantik_api_request(
        method="DELETE",
        end_point=f"/mantik-api/projects/"
        f"{str(project_id)}/data/{str(data_repository_id)}",
        status_code=status_code,
        json_response={},
        expected_error=expected,
    ) as (m, error):
        mantik_api.delete_data_repository(
            project_id=project_id,
            data_repository_id=data_repository_id,
            token="test_token",
        )
        assert any(
            f"Data repository with ID: {data_repository_id} has been deleted"
            in message
            for message in info_caplog.messages
        )
    if error:
        assert any(
            "Call to Mantik API" in message for message in info_caplog.messages
        )


@pytest.mark.parametrize(
    ("status_code", "expected"), [(200, None), (404, requests.HTTPError())]
)
def test_get_data_repositories(
    mock_mantik_api_request, info_caplog, status_code, expected
):
    project_id = uuid.uuid4()
    name = "data_repo_name"
    with mock_mantik_api_request(
        method="GET",
        end_point=f"/mantik-api/projects/{str(project_id)}/data",
        status_code=status_code,
        json_response={
            "totalRecords": 1,
            "dataRepositories": [
                {
                    "dataRepositoryId": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                    "dataRepositoryName": name,
                    "uri": "string",
                    "accessToken": "string",
                    "description": "string",
                    "labels": [
                        {
                            "labelId": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                            "scope": "string",
                            "name": "string",
                            "value": "string",
                        }
                    ],
                }
            ],
        },
        expected_error=expected,
    ) as (m, error):
        data_repositories = mantik_api.get_data_repositories(
            project_id=project_id, token="test_token"
        )
        assert data_repositories[0]["dataRepositoryName"] == name
    if error:
        assert any(
            "Call to Mantik API" in message for message in info_caplog.messages
        )


@pytest.mark.parametrize(
    ("status_code", "expected"), [(200, None), (404, requests.HTTPError())]
)
def test_get_connection(
    mock_mantik_api_request, info_caplog, status_code, expected
):
    user_id = uuid.uuid4()
    connection_id = uuid.uuid4()
    name = "unicore_connection"
    with mock_mantik_api_request(
        method="GET",
        end_point=f"/mantik-api/users/{user_id}/settings/connections/{connection_id}",  # noqa
        status_code=status_code,
        json_response={
            "connectionId": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
            "user": {
                "userId": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "name": "test-name",
                "email": "email-test",
            },
            "connectionName": name,
            "connectionProvider": "string",
            "authMethod": "string",
            "loginName": "string",
            "password": "string",
            "token": "string",
        },
        expected_error=expected,
    ) as (m, error):
        connection = mantik_api.get_connection(
            user_id=user_id, connection_id=connection_id, token="test_token"
        )
        assert connection.connection_name == name
    if error:
        assert any(
            "Call to Mantik API" in message for message in info_caplog.messages
        )


@pytest.mark.parametrize(
    ("env_vars", "expected"),
    [
        (
            {mantik_api._MANTIK_API_URL_ENV_VAR: "https://api.cloud.mantik.ai"},
            "https://api.cloud.mantik.ai",
        ),
        (
            {mlflow.TRACKING_URI_ENV_VAR: "https://tracking.cloud.mantik.ai"},
            "https://api.cloud.mantik.ai",
        ),
        ({}, mantik_api._DEFAULT_MANTIK_API_URL),
    ],
)
def test_get_base_url(env_vars_set, env_vars, expected):
    with env_vars_set(env_vars):
        result = mantik_api._get_base_url()

    assert result == expected
