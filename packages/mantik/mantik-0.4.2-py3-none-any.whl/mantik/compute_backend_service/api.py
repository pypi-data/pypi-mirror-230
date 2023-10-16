"""API routes for compute backend service."""
import contextlib
import json
import logging
import tempfile
import typing as t

import fastapi

import mantik.compute_backend_service._bearer as _bearer
import mantik.compute_backend_service.backend as backend
import mantik.compute_backend_service.exceptions as exceptions
import mantik.compute_backend_service.models as models
import mantik.compute_backend_service.settings as settings

TOKEN_VERIFIER = _bearer.JWTBearer()

SUBMIT_PATH = "/submit"

router = fastapi.APIRouter(dependencies=[fastapi.Depends(TOKEN_VERIFIER)])

logger = logging.getLogger()


@router.post(f"{SUBMIT_PATH}/{{experiment_id}}", status_code=201)
async def submit_run(
    experiment_id: str,
    run_name: str = fastapi.Form(...),
    entry_point: str = fastapi.Form(...),
    mlflow_parameters: t.Optional[str] = fastapi.Form(None),
    unicore_user: str = fastapi.Form(...),
    compute_budget_account: str = fastapi.Form(...),
    unicore_password: str = fastapi.Form(...),
    compute_backend_config: str = fastapi.Form("compute-backend-config.json"),
    mlflow_tracking_uri: str = fastapi.Form(...),
    mlflow_tracking_token: str = fastapi.Form(...),
    mlproject_zip: fastapi.UploadFile = fastapi.File(...),
    app_settings: settings.Settings = fastapi.Depends(settings.get_settings),
) -> models.SubmitRunResponse:
    """
    Submit a run for execution.

    Parameters
    ----------
    experiment_id: Experiment ID.
    run_name: Name of the run
    entry_point: Mlflow project entry point.
    mlflow_parameters: Mlflow project parameters as string holding json.
    unicore_user: UNICORE username.
    compute_budget_account: UNICORE compute project.
    unicore_password: UNICORE password.
    compute_backend_config: Path to UNICORE backend config in zip file.
    mlproject_zip: Zipped Mlflow project directory.

    Returns
    -------
    RunSubmitResponse.

    Notes
    -----
    Credentials for UNICORE are submitted here. They are protected iff https
      is enabled, since form data are encrypted.
    Since we have no build service (so far) only zipped directories can be
      submitted.
    """
    parameters_json = json.loads(mlflow_parameters)
    async with _read_upload_file_if_not_too_large(
        upload_file=mlproject_zip, max_size=app_settings.max_file_size
    ) as zipped:
        response = backend.handle_submit_run_request(
            run_name=run_name,
            experiment_id=experiment_id,
            entry_point=entry_point,
            mlflow_parameters=parameters_json,
            unicore_user=unicore_user,
            compute_budget_account=compute_budget_account,
            unicore_password=unicore_password,
            compute_backend_config=compute_backend_config,
            mlflow_tracking_uri=mlflow_tracking_uri,
            mlflow_tracking_token=mlflow_tracking_token,
            mlproject_zip=zipped,
        )

    return response


@contextlib.asynccontextmanager
async def _read_upload_file_if_not_too_large(
    upload_file: fastapi.UploadFile, max_size: int
) -> t.IO:
    outfile: t.IO = tempfile.TemporaryFile("wb+")
    try:
        size = 0
        chunk = await upload_file.read(1024)
        while chunk:
            size += len(chunk)
            if size > max_size:
                outfile.close()
                raise exceptions.RequestEntityTooLargeException(
                    max_size=max_size
                )
            outfile.write(chunk)
            chunk = await upload_file.read(1024)
        outfile.seek(0)  # Reset stream position
        yield outfile
    finally:
        outfile.close()
