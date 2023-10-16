import logging
import typing as t
import uuid

import requests

import mantik.utils as utils
import mantik.utils.mantik_api.connection as connection
import mantik.utils.mantik_api.credentials as credentials
import mantik.utils.mantik_api.data_repository as data_repository

_MANTIK_API_URL_ENV_VAR = "MANTIK_API_URL"
_MANTIK_API_SUBDOMAIN = "api"
_DEFAULT_MANTIK_API_URL = f"https://{_MANTIK_API_SUBDOMAIN}.cloud.mantik.ai"

_TOKENS_API_PATH_PREFIX = "/mantik-api/mantik/tokens"
MANTIK_API_CREATE_TOKEN_API_PATH = f"{_TOKENS_API_PATH_PREFIX}/create"
MANTIK_API_REFRESH_TOKEN_API_PATH = f"{_TOKENS_API_PATH_PREFIX}/refresh"

logger = logging.getLogger(__name__)


def create_data_repository(
    add_data_repository: data_repository.AddDataRepositoryModel,
    project_id: uuid.UUID,
    token: str,
):
    data = add_data_repository.to_dict()
    endpoint = f"/mantik-api/projects/{str(project_id)}/data"
    response = _send_request_to_mantik_api("POST", data, endpoint, token)
    logger.info(
        f'A new data repository with ID: {response.json()["dataRepositoryId"]} '
        f"and name: {add_data_repository.data_repository_name} at "
        f"{add_data_repository.uri} has been created"
    )


def delete_data_repository(
    project_id: uuid.UUID,
    data_repository_id: uuid.UUID,
    token: str,
):
    data = {}
    endpoint = (
        f"/mantik-api/projects/{str(project_id)}/data/{str(data_repository_id)}"
    )
    _send_request_to_mantik_api("DELETE", data, endpoint, token)
    logger.info(
        f"Data repository with ID: {data_repository_id} has been deleted"
    )


def get_data_repositories(
    project_id: uuid.UUID,
    token: str,
) -> t.List[t.Dict]:
    endpoint = f"/mantik-api/projects/{str(project_id)}/data"
    response = _send_request_to_mantik_api("GET", {}, endpoint, token)
    return response.json()["dataRepositories"]


def get_connection(
    user_id: uuid.UUID,
    connection_id: uuid.UUID,
    token: str,
) -> connection.Connection:
    endpoint = (
        f"/mantik-api/users/{user_id}/settings/connections/{connection_id}"
    )
    response = _send_request_to_mantik_api("GET", {}, endpoint, token).json()

    return connection.Connection(**response)


def create_tokens(
    access_credentials: t.Optional[credentials.Credentials] = None,
) -> t.Dict:
    """Get tokens from the Mantik API."""
    if access_credentials is None:
        access_credentials = credentials.Credentials.from_env()
    response = _send_request_to_mantik_api(
        "POST", access_credentials.to_dict(), MANTIK_API_CREATE_TOKEN_API_PATH
    )
    return response.json()


def refresh_tokens(
    refresh_token: str,
    access_credentials: t.Optional[credentials.Credentials] = None,
) -> t.Dict:
    """Get tokens from the Mantik API."""
    if access_credentials is None:
        access_credentials = credentials.Credentials.from_env()
    data = {
        **access_credentials.to_dict(include_password=False),
        "refresh_token": refresh_token,
    }
    response = _send_request_to_mantik_api(
        "POST", data, MANTIK_API_REFRESH_TOKEN_API_PATH
    )
    return response.json()


def _send_request_to_mantik_api(
    method: str,
    data: dict,
    url_endpoint: str,
    token: t.Optional[str] = None,
) -> requests.Response:
    url = _create_url(url_endpoint)
    header = (
        {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
        }
        if token
        else None
    )
    request = {"url": url, "json": data, "headers": header}
    try:
        response = requests.request(method, **request)
        response.raise_for_status()
    except requests.HTTPError:
        logger.exception(
            "Call to Mantik API %s with data %s failed",
            url,
            data,
            exc_info=True,
        )
        raise
    else:
        return response


def _create_url(endpoint: str) -> str:
    url = _get_base_url()
    with_https = utils.urls.ensure_https_and_remove_double_slashes_from_path(
        f"{url}{endpoint}"
    )
    return with_https


def _get_base_url() -> str:
    """Gets the base URL for the mantik API.

    Notes
    -----
    Tries to get the base URL from (in order)

    1. `MANTIK_API_URL` env var
    2. `MLFLOW_TRACKING_URI` env var
       Replaces the first subdomain with the specified subdomain of the API.

    Defaults to `https://api.cloud.mantik.ai`


    """
    mantik_api_url = utils.env.get_optional_env_var(_MANTIK_API_URL_ENV_VAR)
    if mantik_api_url is not None:
        logger.debug("Base URL for mantik API is set to %s", mantik_api_url)
        return mantik_api_url

    mlflow_tracking_url = utils.env.get_optional_env_var(
        utils.mlflow.TRACKING_URI_ENV_VAR
    )
    if mlflow_tracking_url is not None:
        with_subdomain = utils.urls.replace_first_subdomain(
            mlflow_tracking_url, replace_with=_MANTIK_API_SUBDOMAIN
        )
        logger.debug("Base URL for mantik API is set to %s", with_subdomain)
        return with_subdomain
    logger.debug(
        "Base URL for mantik API is set to %s", _DEFAULT_MANTIK_API_URL
    )
    return _DEFAULT_MANTIK_API_URL
