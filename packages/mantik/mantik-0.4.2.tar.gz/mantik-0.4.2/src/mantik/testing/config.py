import pathlib
import typing as t

import mantik.unicore.config.core as core
import mantik.unicore.config.environment as environment
import mantik.unicore.config.executable as executable
import mantik.unicore.config.resources as resources
import mantik.unicore.credentials as unicore_credentials

MLFLOW_ENV_TEST_ENV_VAR = "MLFLOW_TESTING_MANTIK_TEST_VAR"

ALL_ENV_VARS = [
    unicore_credentials._USERNAME_ENV_VAR,
    unicore_credentials._PASSWORD_ENV_VAR,
    core._PROJECT_ENV_VAR,
    MLFLOW_ENV_TEST_ENV_VAR,
]

DEFAULT_ENV_VAR_VALUE = "test-val"

EXISTING_FILE = (
    pathlib.Path(__file__).parent / "../../../resources/test-project/recipe.def"
).as_posix()


def _create_apptainer_environment(
    path: pathlib.Path,
    type: str = None,
    variables: t.Optional[t.Dict] = None,
    modules: t.Optional[t.List] = None,
    preRunCommand: t.Optional[environment.Command] = None,
    postRunCommand: t.Optional[environment.Command] = None,
    include_mlflow_env_vars: bool = True,
) -> environment.Environment:
    if type is None:
        type = "local"
    if include_mlflow_env_vars:
        variables = _include_mlflow_env_vars(variables)

    return environment.Environment(
        execution=executable.Apptainer(
            path=path,
            type=type,
        ),
        variables=variables,
        modules=modules,
        preRunCommand=preRunCommand,
        postRunCommand=postRunCommand,
    )


def _create_python_environment(
    path: pathlib.Path,
    variables: t.Optional[t.Dict] = None,
    modules: t.Optional[t.List] = None,
    preRunCommand: t.Optional[environment.Command] = None,
    postRunCommand: t.Optional[environment.Command] = None,
    include_mlflow_env_vars: bool = True,
) -> environment.Environment:
    if include_mlflow_env_vars:
        variables = _include_mlflow_env_vars(variables)

    return environment.Environment(
        executable.Python(
            path=path,
        ),
        variables=variables,
        modules=modules,
        preRunCommand=preRunCommand,
        postRunCommand=postRunCommand,
    )


def _include_mlflow_env_vars(env_variables: t.Optional[t.Dict]) -> t.Dict:
    mlflow_env_vars = {
        MLFLOW_ENV_TEST_ENV_VAR: DEFAULT_ENV_VAR_VALUE,
    }
    if env_variables is None:
        env_variables = mlflow_env_vars
    else:
        env_variables = {**env_variables, **mlflow_env_vars}
    return env_variables


def _create_config(
    resources: resources.Resources,
    api_url: str = "test-url",
    user: str = "test-val",
    password: str = "test-val",
    project: str = "test-val",
    env: t.Optional[environment.Environment] = None,
):
    if env is None:
        env = environment.Environment()
    env.variables = _include_mlflow_env_vars(env.variables)

    return core.Config(
        api_url=api_url,
        user=user,
        password=password,
        project=project,
        resources=resources,
        environment=env,
    )
