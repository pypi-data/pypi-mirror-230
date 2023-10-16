import glob
import pathlib
import tempfile
import unittest.mock

import mantik.compute_backend_service.backend as backend
import mantik.testing as testing
import mantik.unicore.credentials as unicore_credentials
import mantik.utils as utils


@unittest.mock.patch("mlflow.projects.run")
def test_handle_submit_run_request(
    mock_run, submit_run_request_data, submit_run_request_files
):
    mock_run.return_value.run_id = "1"
    mock_run.return_value.job_id = "2"
    with utils.env.env_vars_set({utils.mlflow.TRACKING_URI_ENV_VAR: "foo"}):
        response = backend.handle_submit_run_request(
            **submit_run_request_data, **submit_run_request_files
        )
        assert response
        mock_run.assert_called()
        # Assert that secret environment variables are unset
        testing.env.assert_env_var(unicore_credentials._USERNAME_ENV_VAR, None)


def test_unzip_to_tmp(zipped_content):
    with tempfile.TemporaryDirectory() as directory:
        backend._unzip_to_file(zipped_content, directory)
        files = list(
            map(
                lambda filepath: pathlib.Path(filepath).name,
                glob.glob(directory + "/*.py"),
            )
        )
        assert "main.py" in files
