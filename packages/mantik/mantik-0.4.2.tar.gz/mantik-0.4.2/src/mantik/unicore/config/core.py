import dataclasses
import logging
import pathlib
import typing as t
import uuid

import mantik.unicore.config._base as _base
import mantik.unicore.config._utils as _utils
import mantik.unicore.config.environment as _environment
import mantik.unicore.config.read as read
import mantik.unicore.config.resources as _resources
import mantik.unicore.credentials as _unicore_credentials
import mantik.unicore.job as job_wrapper
import mantik.utils.env as env

_PROJECT_ENV_VAR = "MANTIK_COMPUTE_BUDGET_ACCOUNT"
_UNICORE_AUTH_SERVER_URL_ENV_VAR = "MANTIK_UNICORE_AUTH_SERVER_URL"

logger = logging.getLogger(__name__)


@dataclasses.dataclass
class Config(_base.ConfigObject):
    """The backend config for the UNICORE MLflow backend."""

    api_url: str
    user: str
    password: str
    project: str
    resources: _resources.Resources
    environment: t.Optional[_environment.Environment] = None
    exclude: t.Optional[t.List] = None

    @classmethod
    def _from_dict(
        cls, config: t.Dict, connection_id: t.Optional[uuid.UUID] = None
    ) -> "Config":
        """

        Parameters
        ----------
        config : t.Dict
            the possible keys to specify inside the config dictionary are:
            REQUIRED:
                - UnicoreApiUrl : str
                    URL to the API of the UNICORE HPC used.

                The other required field MANTIK_USERNAME, MANTIK_PASSWORD
                and MANTIK_PROJECT are inferred from the environment.
            OPTIONAL:
                - Resources : dict
                    Dict of parameters specifying the resources
                    to request on the remote system.
                    More info can be found here:
                    https://sourceforge.net/p/unicore/wiki/Job_Description/
                - Environment : dict
                    Used to build a environment.Environment.
                - Exclude : list
                    List of files or file-patterns
                    that are not sent with the job


        Returns
        -------
        mantik.unicore._config.core.Config

        """
        api_url = _utils.get_required_config_value(
            name="UnicoreApiUrl",
            value_type=str,
            config=config,
        )
        unicore_credentials = (
            _unicore_credentials.UnicoreCredentials.get_credentials(
                connection_id
            )
        )
        project = env.get_required_env_var(_PROJECT_ENV_VAR)
        resources = _resources.Resources.from_dict(
            _utils.get_required_config_value(
                name="Resources",
                value_type=dict,
                config=config,
            )
        )
        environment = _utils.get_optional_config_value(
            name="Environment",
            value_type=_environment.Environment.from_dict,
            config=config,
        )
        exclude = _utils.get_optional_config_value(
            name="Exclude",
            value_type=list,
            config=config,
        )

        return cls(
            api_url=api_url,
            user=unicore_credentials.username,
            password=unicore_credentials.password,
            project=project,
            resources=resources,
            environment=environment,
            exclude=exclude,
        )

    def __post_init__(self):
        if self.environment is None:
            self.environment = _environment.Environment()

        # set SRUN_CPUS_PER_TASK to CPUsPerNode if not explicitly set
        self.environment = self.environment.set_srun_cpus_per_task_if_unset(
            self.resources
        )

    @classmethod
    def from_filepath(
        cls, filepath: pathlib.Path, connection_id: t.Optional[uuid.UUID] = None
    ) -> "Config":
        """Initialize from a given file."""
        return cls._from_dict(
            read.read_config(filepath), connection_id=connection_id
        )

    @property
    def files_to_exclude(self) -> t.List[str]:
        return self.exclude or []

    def _to_dict(self) -> t.Dict:
        environment = (
            self.environment.to_dict() if self.environment is not None else {}
        )
        return {
            "Project": self.project,
            "Resources": self.resources,
            # Write stderr/stdout to given file to allow access to logs
            "Stdout": job_wrapper.APPLICATION_LOGS_FILE,
            "Stderr": job_wrapper.APPLICATION_LOGS_FILE,
            **environment,
        }

    def to_job_description(self, arguments: t.List[str]) -> t.Dict:
        """Convert to UNICORE job description."""
        environment = (
            self.environment.to_job_description(arguments)
            if self.environment is not None
            else {}
        )
        return {
            **self.to_dict(),
            **environment,
        }

    def execution_environment_given(self) -> bool:
        return (
            self.environment is not None and self.environment.execution_given()
        )

    def add_env_vars(self, env_vars: t.Dict) -> None:
        self.environment.add_env_vars(env_vars)
