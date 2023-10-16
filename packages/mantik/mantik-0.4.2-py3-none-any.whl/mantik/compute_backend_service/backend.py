"""Backend implementation."""
import pathlib
import typing as t
import zipfile

import mlflow.projects

import mantik.compute_backend_service.models as models
import mantik.unicore.config.core as core
import mantik.unicore.config.read as read
import mantik.unicore.credentials as unicore_credentials
import mantik.utils as utils


@utils.temp_dir.use_temp_dir
def handle_submit_run_request(
    run_name: str,
    experiment_id: str,
    entry_point: str,
    mlflow_parameters: t.Dict,
    unicore_user: str,
    compute_budget_account: str,
    unicore_password: str,
    compute_backend_config: str,
    mlflow_tracking_uri: str,
    mlflow_tracking_token: str,
    mlproject_zip: t.BinaryIO,
    temp_dir_name: t.Optional[str] = None,
) -> models.SubmitRunResponse:
    """
    Handle the submit run request.

    Parameters
    ----------
    run_name: name of the run
    experiment_id: experiment id.
    entry_point: mlflow project entrypoint.
    mlflow_parameters: parameters for the mlflow run -P flag.
    unicore_user: UNICORE username.
    compute_budget_account: UNICORE compute project.
    unicore_password: UNICORE password.
    compute_backend_config: Path to unicore backend config in the zipped
      mlflow project.
    mlflow_tracking_uri: Tracking URI.
    mlflow_tracking_token: Token to permit access to tracking API.
    mlproject_zip: file like object holding zipped mlproject directory.
    temp_dir_name: temporary directory name, used for testing
    Returns
    -------
    Submit run response.
    """
    env_vars = _create_required_env_vars(
        run_name=run_name,
        unicore_user=unicore_user,
        unicore_password=unicore_password,
        compute_budget_account=compute_budget_account,
        mlflow_tracking_uri=mlflow_tracking_uri,
        experiment_id=experiment_id,
        mlflow_tracking_token=mlflow_tracking_token,
    )
    with utils.env.env_vars_set(env_vars):
        _unzip_to_file(mlproject_zip, temp_dir_name)
        backend_config = pathlib.Path(
            f"{temp_dir_name}/{compute_backend_config}"
        )
        # Note: If version is not handed to run method,
        # mlflow throws an error
        version = None
        submitted_run = mlflow.projects.run(
            temp_dir_name,
            entry_point,
            version,
            experiment_id=experiment_id,
            parameters=mlflow_parameters,
            backend="unicore",
            backend_config=read.read_config(backend_config),
            synchronous=False,
        )
    return models.SubmitRunResponse(
        experiment_id=int(experiment_id),
        run_id=submitted_run.run_id,
        unicore_job_id=submitted_run.job_id,
    )


def _create_required_env_vars(
    run_name: str,
    unicore_user: str,
    compute_budget_account: str,
    unicore_password: str,
    mlflow_tracking_uri: str,
    experiment_id: str,
    mlflow_tracking_token: str,
) -> t.Dict[str, str]:
    return {
        unicore_credentials._USERNAME_ENV_VAR: unicore_user,
        core._PROJECT_ENV_VAR: compute_budget_account,
        unicore_credentials._PASSWORD_ENV_VAR: unicore_password,
        utils.mlflow.TRACKING_URI_ENV_VAR: mlflow_tracking_uri,
        utils.mlflow.EXPERIMENT_ID_ENV_VAR: experiment_id,
        utils.mlflow.TRACKING_TOKEN_ENV_VAR: mlflow_tracking_token,
        utils.mlflow.RUN_NAME_ENV_VAR: run_name,
    }


def _unzip_to_file(zipped: t.BinaryIO, file: str) -> None:
    with zipfile.ZipFile(zipped, "r") as zip_ref:
        zip_ref.extractall(file)
