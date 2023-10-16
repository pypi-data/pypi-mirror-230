import pathlib

import pytest

import mantik.unicore.config as config
import mantik.unicore.config.executable as executable

FILE_DIR = pathlib.Path(__file__).parent


@pytest.fixture(scope="function")
def example_config() -> config.core.Config:
    return config.core.Config(
        api_url="test-url",
        user="user",
        password="password",
        project="test-project",
        environment=config.environment.Environment(
            execution=executable.Apptainer(
                path=pathlib.Path("mantik-test.sif"),
            )
        ),
        resources=config.resources.Resources(queue="batch"),
        exclude=["*.sif"],
    )


@pytest.fixture()
def example_project_path() -> pathlib.Path:
    return FILE_DIR / "../../resources/test-project"
