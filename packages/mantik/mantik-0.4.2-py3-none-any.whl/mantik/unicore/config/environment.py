import dataclasses
import os
import re
import typing as t

import mantik.unicore.config._base as _base
import mantik.unicore.config._utils as _utils
import mantik.unicore.config.executable as _executable
import mantik.unicore.config.resources as _resources
import mantik.unicore.exceptions as exceptions
import mantik.utils.mlflow as mlflow

_MLFLOW_ENV_VAR_PREFIX = "MLFLOW_"
_ALLOWED_EXECUTABLES = {
    "Apptainer": _executable.Apptainer,
    "Python": _executable.Python,
}


@dataclasses.dataclass
class Command:
    command: str
    executeOnLoginNode: bool = False

    @classmethod
    def from_dict(cls, config: t.Dict):
        command = _utils.get_optional_config_value(
            name="Command",
            value_type=str,
            config=config,
        )
        executeOnLoginNode = _utils.get_optional_config_value(
            name="ExecuteOnLoginNode",
            value_type=bool,
            config=config,
        )
        return cls(command=command, executeOnLoginNode=executeOnLoginNode)


@dataclasses.dataclass
class Environment(_base.ConfigObject):
    """Part of the backend-config where all variables
    concerning the running environment are stored."""

    execution: t.Optional[_executable.Execution] = None
    variables: t.Optional[t.Dict] = None
    modules: t.Optional[t.List] = None
    preRunCommand: t.Optional[Command] = None
    postRunCommand: t.Optional[Command] = None

    @classmethod
    def _from_dict(cls, config: t.Dict) -> "Environment":
        execution = _get_execution_environment(config)
        variables = _utils.get_optional_config_value(
            name="Variables",
            value_type=dict,
            config=config,
        )
        modules = _utils.get_optional_config_value(
            name="Modules",
            value_type=list,
            config=config,
        )

        preRunCommand = _utils.get_optional_config_value(
            name="PreRunCommand",
            value_type=Command.from_dict,
            config=config,
        )

        postRunCommand = _utils.get_optional_config_value(
            name="PostRunCommand",
            value_type=Command.from_dict,
            config=config,
        )

        return cls(
            execution=execution,
            modules=modules,
            variables=variables,
            preRunCommand=preRunCommand,
            postRunCommand=postRunCommand,
        )

    def __post_init__(self):
        """Add all MLflow environment variables to the environment."""
        self.variables = _add_mlflow_env_vars(self.variables)

    def _to_dict(self) -> t.Dict:
        return {
            "Environment": self.variables,
            "User precommand": self._create_precommand(),
            "RunUserPrecommandOnLoginNode": self._execute_precommand_on_login_node,  # noqa: E501
            "Executable": self._create_execution_command(),
            "Arguments": self._create_arguments(),
            "User postcommand": self._create_postcommand(),
            "RunUserPostcommandOnLoginNode": self._execute_precommand_on_login_node,  # noqa: E501
        }

    def _create_precommand(self) -> t.Optional[str]:
        # Venv MUST be loaded before modules
        # see https://gitlab.com/mantik-ai/mantik/issues/140
        precommand = self.preRunCommand.command if self.preRunCommand else None
        venv_command = (
            self.execution.get_precommand()
            if self.execution is not None
            else None
        )
        modules_command = (
            f"module load {' '.join(self.modules)}" if self.modules else None
        )
        joined_str = "; ".join(
            filter(None, [precommand, venv_command, modules_command])
        )
        return joined_str or None

    @property
    def _execute_precommand_on_login_node(self) -> bool:
        return (
            self.preRunCommand.executeOnLoginNode
            if self.preRunCommand
            else False
        )

    def _create_postcommand(self) -> t.Optional[str]:
        return self.postRunCommand.command if self.postRunCommand else None

    @property
    def _execute_postcommand_on_login_node(self) -> bool:
        return (
            self.postRunCommand.executeOnLoginNode
            if self.postRunCommand
            else False
        )

    def _create_execution_command(self) -> t.Optional[str]:
        if self.execution is not None:
            return self.execution.get_execution_command()
        return

    def _create_arguments(self) -> t.Optional[t.List[str]]:
        if self.execution is not None:
            return self.execution.get_arguments()
        return

    def set_srun_cpus_per_task_if_unset(
        self, resources: _resources.Resources
    ) -> "Environment":
        cpus_per_task = resources.cpus_per_node

        if cpus_per_task is not None:
            if self.variables is None:
                self.variables = {"SRUN_CPUS_PER_TASK": str(cpus_per_task)}
            elif (
                self.variables is not None
                and "SRUN_CPUS_PER_TASK" not in self.variables
            ):
                self.variables["SRUN_CPUS_PER_TASK"] = str(cpus_per_task)

        return self

    def to_job_description(self, arguments: t.List[str]) -> t.Dict:
        """Convert to UNICORE job description.

        Parameters
        ----------
        arguments : list[str]
            Arguments to pass to the executable.

        Returns
        -------
        dict
            The UNICORE job description.

            For details see https://sourceforge.net/p/unicore/wiki/Job_Description  # noqa: E501


        """
        as_dict = self.to_dict()

        if (
            # If no environment or execution is given, the arguments should
            # be split into executable and arguments.
            not self.execution_given()
            # In case of config.Environment.Execution is Python,
            # the ``Executable`` is ``None``. In this case,
            # UNICORE would not execute anything on the compute node,
            # even if ``Arguments`` are given.
            or isinstance(self.execution, _executable.Python)
        ):
            (
                executable,
                arguments,
            ) = _split_arguments_to_executable_and_arguments(arguments)
            return {
                **as_dict,
                "Executable": executable,
                "Arguments": arguments,
            }
        elif isinstance(self.execution, _executable.Apptainer):
            # In case of Apptainer environment, just append the arguments
            as_dict["Arguments"].extend(arguments)
            return as_dict
        raise NotImplementedError(
            f"Environment of type {type(self.execution)} not implemented"
        )

    def execution_given(self) -> bool:
        return self.execution is not None

    def add_env_vars(self, env_vars: t.Dict) -> None:
        if self.variables is None:
            self.variables = env_vars
        else:
            self.variables.update(env_vars)


def _get_execution_environment(
    config: t.Dict,
) -> t.Optional[_executable.Execution]:
    envs = [env for env in _ALLOWED_EXECUTABLES if env in config]
    execution = _get_only_one_environment_or_none(envs)
    if execution is not None:
        return execution.from_dict(config)
    return


def _get_only_one_environment_or_none(
    env_found: t.List,
) -> t.Optional[t.Type[_executable.Execution]]:
    if not env_found:
        return None
    elif len(env_found) > 1:
        raise exceptions.ConfigValidationError(
            "Only one execution environment is allowed, "
            "but in config these have been found: "
            f"{exceptions.iterable_to_string(env_found)}."
        )

    try:
        return _ALLOWED_EXECUTABLES[env_found[0]]
    except KeyError as e:
        raise ValueError(
            f"Environment of type {env_found} not supported"
        ) from e


def _add_mlflow_env_vars(environment: t.Optional[t.Dict]) -> t.Optional[t.Dict]:
    mlflow_env_vars = _get_mlflow_env_vars()
    if mlflow_env_vars:
        if environment is None:
            return mlflow_env_vars
        return {**mlflow_env_vars, **environment}
    return environment


def _get_mlflow_env_vars() -> t.Dict:
    pattern = re.compile(rf"{_MLFLOW_ENV_VAR_PREFIX}\w+")
    return {
        key: value
        for key, value in os.environ.items()
        if pattern.match(key) and key not in mlflow.CONFLICTING_ENV_VARS
    }


def _split_arguments_to_executable_and_arguments(
    arguments: t.List[str],
) -> t.Tuple[str, t.List[str]]:
    return arguments[0], arguments[1:]
