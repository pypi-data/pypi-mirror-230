import contextlib
import os
import pathlib
import typing as t

import mlflow.projects._project_spec
import pytest

FILE_DIR = pathlib.Path(__file__).parent


@pytest.fixture
def env_vars_set():
    @contextlib.contextmanager
    def wrapped(env_vars: t.Dict[str, t.Any]):
        for key, value in env_vars.items():
            os.environ[key] = value
        yield
        for key in env_vars:
            try:
                os.environ.pop(key)
            except KeyError:
                pass

    return wrapped


@pytest.fixture
def expect_raise_if_exception() -> (
    t.Callable[[t.Any], contextlib.AbstractContextManager]
):
    def expect_can_be_error(
        expected: t.Any,
    ) -> contextlib.AbstractContextManager:
        return (
            pytest.raises(type(expected))
            if isinstance(expected, Exception)
            else contextlib.nullcontext()
        )

    return expect_can_be_error


@pytest.fixture()
def example_project_path() -> pathlib.Path:
    return FILE_DIR / "resources/test-project"


@pytest.fixture()
def example_project(
    example_project_path,
) -> mlflow.projects._project_spec.Project:
    return mlflow.projects.utils.load_project(example_project_path)
