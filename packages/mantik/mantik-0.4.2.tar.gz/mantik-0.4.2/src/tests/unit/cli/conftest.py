import pathlib

import pytest

FILE_DIR = pathlib.Path(__file__).parent


@pytest.fixture()
def example_project_path() -> str:
    return (FILE_DIR / "../../resources/test-project").as_posix()
