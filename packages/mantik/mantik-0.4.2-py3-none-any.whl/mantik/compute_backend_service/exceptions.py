import fastapi.exceptions
import mlflow.exceptions
import requests.exceptions as request_exceptions
import starlette.status as status

import mantik.compute_backend_service.settings as settings
import mantik.unicore.exceptions as _exceptions


async def internal_exception_handler(
    request: fastapi.Request, exc: _exceptions.UnicoreError  # noqa
) -> fastapi.responses.JSONResponse:
    return fastapi.responses.JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"message": "Mantik Internal Server Error"},
    )


async def unicore_exception_handler(
    request: fastapi.Request, exc: _exceptions.UnicoreError  # noqa
) -> fastapi.responses.JSONResponse:
    return fastapi.responses.JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"message": f"Unicore backend error. Cause: {str(exc)}"},
    )


async def config_validation_exception_handler(
    request: fastapi.Request, exc: _exceptions.ConfigValidationError  # noqa
) -> fastapi.responses.JSONResponse:
    return fastapi.responses.JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "message": "While submitting the job, "
            f"this configuration error occurred: {str(exc)}"
        },
    )


async def request_exception_handler(
    request: fastapi.Request, exc: request_exceptions.HTTPError  # noqa
) -> fastapi.responses.JSONResponse:
    return fastapi.responses.JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "message": "While submitting the job, "
            f"this request error occurred: {str(exc)}"
        },
    )


async def connection_exception_handler(
    request: fastapi.Request, exc: ConnectionError  # noqa
) -> fastapi.responses.JSONResponse:
    return fastapi.responses.JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "message": "While submitting the job, "
            f"this connection error occurred: {str(exc)}"
        },
    )


async def mlflow_exception_handler(
    request: fastapi.Request, exc: mlflow.exceptions.MlflowException  # noqa
) -> fastapi.responses.JSONResponse:
    return fastapi.responses.JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "message": "While submitting the job, "
            f"this mlflow error occurred: {str(exc)}"
        },
    )


class RequestEntityTooLargeException(fastapi.exceptions.HTTPException):
    """Files that are sent are too large to be handled."""

    def __init__(self, max_size: int = settings.DEFAULT_MAX_SIZE):
        super().__init__(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE)
        self.max_size = max_size


async def file_too_large_exception_handler(
    request: fastapi.Request, exc: RequestEntityTooLargeException  # noqa
) -> fastapi.responses.JSONResponse:
    return fastapi.responses.JSONResponse(
        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
        content={
            "message": f"The files you sent were too large to be handled by "
            f"the API. Consider using scp for direct file "
            f"transfer to remote compute resources. "
            f"The maximum allowed size is {float(exc.max_size)/1048576.} MB."
        },
    )
