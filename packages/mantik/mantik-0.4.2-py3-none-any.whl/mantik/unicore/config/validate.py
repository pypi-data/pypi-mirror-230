import logging
import pathlib
import typing as t

import mlflow

import mantik.unicore.config.core as core
import mantik.unicore.config.executable as executable
import mantik.unicore.exceptions as exceptions
import mantik.unicore.utils as utils

logger = logging.getLogger(__name__)


class ProjectValidator:
    def __init__(
        self,
        mlproject_path: t.Union[pathlib.Path, str],
        config_path: t.Union[pathlib.Path, str],
        mlflow_parameters: t.Dict,
        entry_point: str,
        logger_level: int = logging.WARNING,
    ):
        self.mlproject_path = pathlib.Path(mlproject_path)
        self.config_path = pathlib.Path(config_path)
        self.mlflow_parameters = mlflow_parameters
        self.entry_point = entry_point
        logger.setLevel(logger_level)

        self._config = None

    @property
    def config(self) -> core.Config:
        if self._config is None:
            self._config = core.Config.from_filepath(self.config_absolute_path)
        return self._config

    @property
    def config_absolute_path(self) -> pathlib.Path:
        return (
            self.config_path
            if self.config_path.is_absolute()
            else self.mlproject_path / self.config_path
        )

    @property
    def config_relative_path(self) -> pathlib.Path:
        return (
            self.config_path
            if not self.config_path.is_absolute()
            else self.config_path.relative_to(self.mlproject_path)
        )

    def validate(self) -> None:
        logger.debug(
            "Validating MLproject at %s and backend config at %s",
            self.mlproject_path.as_posix(),
            self.config_absolute_path.as_posix(),
        )
        if not self.mlproject_path.is_absolute():
            raise exceptions.ConfigValidationError(
                "ML project path must be an absolute path, "
                f"but {self.mlproject_path.as_posix()!r} was given."
            )
        if not self.mlproject_path.is_dir():
            raise exceptions.ConfigValidationError(
                "ML project path not found at "
                f"{self.mlproject_path.as_posix()!r}, "
                "check that the given path is correct."
            )
        if not self.config_absolute_path.is_file():
            raise exceptions.ConfigValidationError(
                "Config not found at "
                f"{self.config_absolute_path.as_posix()!r}, "
                "check that the given path is correct."
            )
        if not (self.mlproject_path in self.config_absolute_path.parents):
            raise exceptions.ConfigValidationError(
                "Config file is not in the ML project directory, "
                "check that the given paths are correct:\n"
                f"Config file: {self.config_absolute_path.as_posix()!r}\n"
                f"ML project directory: {self.mlproject_path.as_posix()!r}"
            )
        if self.config.execution_environment_given():
            self._validate_execution_path(self.config.environment.execution)
        logger.debug("Validating MLproject configuration.")
        self._validate_ml_project_file()
        self._validate_config_not_in_exclude()

    def _validate_execution_path(self, execution: executable.Execution):
        if execution.path_has_to_be_checked:
            execution_absolute_path = self.mlproject_path / execution.path
            if not execution_absolute_path.is_file():
                raise exceptions.ConfigValidationError(
                    f"The path {execution_absolute_path.as_posix()!r} given "
                    "as execution environment was not found, "
                    "check that the given path is correct. "
                    "The path must be relative to the ML project path."
                )

    def _validate_ml_project_file(self):
        return pathlib.Path(
            mlflow.projects.utils.fetch_and_validate_project(
                uri=self.mlproject_path.as_posix(),
                version=None,
                entry_point=self.entry_point,
                parameters=self.mlflow_parameters,
            )
        )

    def _validate_config_not_in_exclude(self) -> None:
        if utils.upload.file_matches_exclude_pattern(
            path=self.config_absolute_path,
            project_dir=self.mlproject_path,
            exclude=self.config.files_to_exclude,
        ):
            raise exceptions.ConfigValidationError(
                f"Config file '{self.config_path.name}' cannot be excluded, "
                f"check config 'Exclude' section"
            )
