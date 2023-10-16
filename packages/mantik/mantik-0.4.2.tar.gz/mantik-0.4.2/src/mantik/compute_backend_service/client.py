import dataclasses
import json
import logging
import pathlib
import typing as t
import uuid

import requests

import mantik
import mantik.cli as cli
import mantik.compute_backend_service.api as api
import mantik.unicore.config.core as core
import mantik.unicore.config.validate as validate
import mantik.unicore.credentials as _unicore_credentials
import mantik.unicore.utils.zip as unicore_zip
import mantik.utils as utils

logger = logging.getLogger(__name__)

_DEFAULT_COMPUTE_BACKEND_API_PATH = "/compute-backend"
_DEFAULT_COMPUTE_BACKEND_SUBDOMAIN = "computebackend"
_COMPUTE_BACKEND_SUBDOMAIN = utils.env.get_optional_env_var(
    "COMPUTE_BACKEND_SUB_DOMAIN", default=_DEFAULT_COMPUTE_BACKEND_SUBDOMAIN
)


@dataclasses.dataclass
class ComputeBackendClient:
    """Client for the compute backend.

    Parameters
    ----------
    compute_backend_url : str
        URL of the compute backend API.
    unicore_username : str
        UNICORE username.
    unicore_password : str
        Password for the respective UNICORE user.
    compute_budget_account : str
        Project to use for the compute budget.
    mlflow_tracking_uri : str
        URI of the MLflow tracking server.
    mlflow_tracking_token : str
        Authentication token for the MLflow tracking server.
    api_path : str, default="/compute-backend"
        API path of the compute backend.
        E.g. if `compute_backend_url="https://<host>.com"`, but the actual API
        listens at `https://<host>.com/any/path`, this path can be given here,
        i.e. `api_path=/any/path`.

    """

    compute_backend_url: str
    unicore_username: str
    unicore_password: str
    compute_budget_account: str
    mlflow_tracking_uri: str
    mlflow_tracking_token: str
    api_path: str = _DEFAULT_COMPUTE_BACKEND_API_PATH

    @classmethod
    def from_env(
        cls,
        api_path: str = _DEFAULT_COMPUTE_BACKEND_API_PATH,
        connection_id: t.Optional[uuid.UUID] = None,
    ) -> "ComputeBackendClient":
        """Create from environment variables."""
        unicore_credentials = (
            _unicore_credentials.UnicoreCredentials.get_credentials(
                connection_id
            )
        )
        compute_budget_account = mantik.utils.env.get_required_env_var(
            core._PROJECT_ENV_VAR
        )
        mlflow_tracking_uri = mantik.utils.env.get_required_env_var(
            utils.mlflow.TRACKING_URI_ENV_VAR
        )
        environment = mantik.tracking.track.init_tracking()
        return cls(
            compute_backend_url=mlflow_tracking_uri,
            unicore_username=unicore_credentials.username,
            unicore_password=unicore_credentials.password,
            compute_budget_account=compute_budget_account,
            mlflow_tracking_uri=mlflow_tracking_uri,
            mlflow_tracking_token=environment.token,
            api_path=api_path,
        )

    def __post_init__(self):
        """Ensure Compute Backend URL contains the correct subdomain."""
        with_path_prefix = f"{self.compute_backend_url}/{self.api_path}"
        with_sub_domain = utils.urls.replace_first_subdomain(
            with_path_prefix, replace_with=_COMPUTE_BACKEND_SUBDOMAIN
        )
        with_https = (
            utils.urls.ensure_https_and_remove_double_slashes_from_path(
                with_sub_domain
            )
        )
        self.compute_backend_url = with_https
        logger.debug("Client initialized")

    @property
    def url(self) -> str:
        """Return the API URL of the compute backend."""
        return self.compute_backend_url

    @property
    def submit_url(self) -> str:
        """Return the API URL for the submit endpoint."""
        return f"{self.url}{api.SUBMIT_PATH}"

    def submit_run(
        self,
        run_name: str,
        experiment_id: int,
        mlproject_path: t.Union[pathlib.Path, str],
        mlflow_parameters: t.Dict,
        backend_config: t.Union[pathlib.Path, str],
        entry_point: t.Optional[str] = None,
    ) -> requests.Response:
        """Submit a run.

        Parameters
        ----------
        run_name: str
            Name of the run
        experiment_id : int
            ID of the tracking experiment.
        mlproject_path : pathlib.Path
            Path to the MLproject directory.
        mlflow_parameters : dict
            Parameters to pass to the MLproject.
        backend_config : pathlib.Path
            Path within the MLproject directory to the backend config.
            E.g. `backend-config.json`.
        entry_point : str, default="main"
            Name of the entry point to execute.

        Returns
        -------
        requests.Response
            The response of the compute backend.

        """
        if entry_point is None:
            entry_point = "main"
        logger.debug(
            "Submitting MLproject %s for experiment %s",
            mlproject_path,
            experiment_id,
        )
        project_validator = validate.ProjectValidator(
            mlproject_path=mlproject_path,
            config_path=backend_config,
            mlflow_parameters=mlflow_parameters,
            entry_point=entry_point,
            logger_level=logger.level,
        )
        project_validator.validate()
        url = f"{self.submit_url}/{experiment_id}"
        data = self._generate_request_data(
            run_name=run_name,
            entry_point=entry_point,
            mlflow_parameters=mlflow_parameters,
            compute_backend_config=project_validator.config_relative_path.as_posix(),  # noqa
        )
        files = _generate_request_files(
            mlproject_path=project_validator.mlproject_path,
            config=project_validator.config,
        )
        headers = self._generate_headers()
        logger.debug(
            "Sending request to compute backend %s with headers %s and data %s",
            url,
            headers,
            data,
        )
        try:
            response = requests.post(
                url=url,
                headers=headers,
                data=data,
                files=files,
            )
            response.raise_for_status()
        except requests.HTTPError as e:
            logger.exception(
                "Job submission failed (%s): %s", e.response, e.response.content
            )
            if e.response.status_code == 413:
                message = (
                    "The files you submitted were too large. "
                    "Please consider transferring large files "
                    "(such as image files) manually using the "
                    "Mantik Remote File Service CLI. "
                    "(See mantik "
                    f"{cli.remote_file_service.unicore_file_service.GROUP_NAME} "  # noqa: E501
                    "--help). "
                    "You will also have to change the backend "
                    "configuration to use a remote image. "
                    "Then you can try to re-submit the job."
                )
            else:
                try:
                    message = e.response.json()["message"]
                except (KeyError, json.decoder.JSONDecodeError) as e:
                    message = e.response.text
            raise requests.HTTPError(f"Job submission failed: {message}") from e
        else:
            (
                experiment_id,
                run_id,
                unicore_job_id,
            ) = _extract_job_info_from_response_json(response.json())
            logger.debug(
                "Job submitted successful with experiment_id=%s,"
                " run_id=%s, unicore_job_id=%s.",
                experiment_id,
                run_id,
                unicore_job_id,
            )
            return response

    def _generate_headers(self):
        return {
            "Authorization": f"Bearer {self.mlflow_tracking_token}",
            "Accept": "application/json",
        }

    def _generate_request_data(
        self,
        run_name: str,
        entry_point: str,
        mlflow_parameters: t.Dict,
        compute_backend_config: str,
    ) -> t.Dict:
        return {
            "run_name": run_name,
            "entry_point": entry_point,
            "mlflow_parameters": json.dumps(mlflow_parameters),
            "unicore_user": self.unicore_username,
            "unicore_password": self.unicore_password,
            "compute_budget_account": self.compute_budget_account,
            "compute_backend_config": compute_backend_config,
            "mlflow_tracking_uri": self.mlflow_tracking_uri,
            "mlflow_tracking_token": self.mlflow_tracking_token,
        }


def _generate_request_files(
    mlproject_path: pathlib.Path, config: core.Config
) -> t.Dict:
    logger.debug("Zipping MLproject directory %s", mlproject_path)
    zipped = unicore_zip.zip_directory_with_exclusion(mlproject_path, config)
    return {"mlproject_zip": zipped.read()}


def _extract_job_info_from_response_json(
    response_json: t.Dict,
) -> t.Tuple[str, str, str]:
    experiment_id = response_json.get("experiment_id")
    run_id = response_json.get("run_id")
    unicore_job_id = response_json.get("unicore_job_id")
    return experiment_id, run_id, unicore_job_id
