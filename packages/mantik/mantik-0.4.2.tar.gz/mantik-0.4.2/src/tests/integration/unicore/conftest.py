import os
import pathlib

import pytest

FILE_DIR = pathlib.Path(__file__).parent


@pytest.fixture()
def unicore_api_url() -> str:
    # Allow reading from env var for CI testing
    return os.getenv(
        "UNICORE_API_TESTING_URL", "https://localhost:8080/DEMO-SITE/rest/core"
    )


@pytest.fixture()
def unicore_credentials() -> dict:
    # Username and password are provided in
    # https://github.com/UNICORE-EU/tools/blob/master/unicore-docker-image/README.md
    return {
        "user": "demouser",
        "password": "test123",
    }


@pytest.fixture()
def example_project_with_batch_script_path() -> pathlib.Path:
    return FILE_DIR / "../../resources/test-project-with-batch-script"
