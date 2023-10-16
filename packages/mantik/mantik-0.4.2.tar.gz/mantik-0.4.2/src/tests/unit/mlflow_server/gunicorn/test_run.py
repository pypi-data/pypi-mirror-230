import pytest

import mantik.mlflow_server.gunicorn.run as run


@pytest.mark.parametrize(
    "argv",
    [
        [],
        ["--testing"],
        ["--artifacts-destination", "test-destination"],
        ["--artifacts-destination", "test-destination", "--serve-artifacts"],
    ],
)
def test_run(tmp_path, argv):
    run._create_app([*argv, "--backend-store-uri", tmp_path.as_posix()])
