"""Mantik UNICORE plugin for MLflow."""
import logging
import pathlib
import typing as t

import mlflow.projects as projects
import mlflow.projects._project_spec as _project_spec
import mlflow.projects.backend as mlflow_backend

import mantik.unicore._connect as _connect
import mantik.unicore.client as client_wrapper
import mantik.unicore.config.core as core
import mantik.unicore.job as job_wrapper
import mantik.unicore.submitted_run as submitted_run
import mantik.unicore.utils.upload as upload
import mantik.utils.env as env
import mantik.utils.mlflow as mlflow_utils

logger = logging.getLogger(__name__)


class UnicoreBackend(mlflow_backend.AbstractBackend):
    """UNICORE backend for running MLflow projects."""

    def run(
        self,
        project_uri: str,
        entry_point: str,
        params: t.Dict,
        version: t.Optional[str],
        backend_config: t.Dict,
        tracking_uri: str,
        experiment_id: str,
    ) -> submitted_run.SubmittedUnicoreRun:
        """Run an entrypoint.

        It must return a SubmittedRun object to track the execution

        Parameters
        ----------
        project_uri : str
            URI of the project to execute.

            E.g. a local filesystem path or a Git repository URI like
            https://github.com/mlflow/mlflow-example
        entry_point : str
            Entry point to run within the project.

            E.g. for a project that is defined as

            .. code-block:: yaml
               :caption: MLproject entry points

               entry_points:
                   main:
                     parameters:
                       print: {type: "string", default: "test"}
                     command: python main.py {print}

            the `entry_point="main"`.
        params : dict
            Dict of parameters to pass to the entry point.

            For the example entrypoint as above, if the project is run as
            `mlflow run --backend unicore <project path> -P print=hi`, this
            would be `{"print": "hi"}`.
        version : str
            For git-based projects, either a commit hash or a branch name.
        backend_config : dict
            The backend config.

            By default, mlflow passes the following dict

            .. code-block:: python
               :caption: Default MLflow ``backend_config``

               {
                'DOCKER_ARGS': {},
                'STORAGE_DIR': None,
                'SYNCHRONOUS': False,
                'USE_CONDA': True,
               }

            which is extended by the content given in the backend
            config of a user.
        tracking_uri : str
            URI of tracking server against which to log run information.

            E.g. for local tracking this may be
            `'file://<home path>/mantik/mlruns'`
        experiment_id : str
            ID of experiment under which to launch the run.

            E.g. `'0'` for the Default experiment that is created by mlflow.

        Returns
        -------
        mantik.unicore.submitted_run.SubmittedUnicoreRun

        """
        project_dir, project = _load_project(
            project_uri=project_uri,
            version=version,
            entry_point=entry_point,
            parameters=params,
        )

        run_id = _create_active_run(
            project_uri=project_uri,
            experiment_id=experiment_id,
            project_dir=project_dir,
            version=version,
            entry_point=entry_point,
            parameters=params,
        )

        run = _submit_run(
            run_id=run_id,
            backend_config=backend_config,
            project_dir=project_dir,
            project=project,
            entry_point=entry_point,
            parameters=params,
        )
        return run


def _load_project(
    project_uri: str,
    entry_point: str,
    parameters: t.Dict,
    version: t.Optional[str] = None,
) -> t.Tuple[pathlib.Path, _project_spec.Project]:
    project_dir = pathlib.Path(
        projects.utils.fetch_and_validate_project(
            uri=project_uri,
            version=version,
            entry_point=entry_point,
            parameters=parameters,
        )
    )
    project = projects.utils.load_project(project_dir)
    logger.info(f"Loaded project {project.name}")
    return project_dir, project


def _create_active_run(
    project_uri: str,
    experiment_id: str,
    project_dir: pathlib.Path,
    entry_point: str,
    parameters: t.Dict,
    version: t.Optional[str] = None,
) -> str:
    run_name = env.get_required_env_var(mlflow_utils.RUN_NAME_ENV_VAR)
    active_run = mlflow_utils.create_run(
        run_name=run_name,
        uri=project_uri,
        experiment_id=experiment_id,
        work_dir=project_dir,
        version=version,
        entry_point=entry_point,
        parameters=parameters,
    )
    run_id = active_run.info.run_id
    logger.info(f"Created new active run {run_id}, with name {run_name}")
    return run_id


def _submit_run(
    run_id: str,
    backend_config: t.Dict,
    project_dir: pathlib.Path,
    project: _project_spec.Project,
    entry_point: str,
    parameters: t.Dict,
) -> submitted_run.SubmittedUnicoreRun:
    job = _prepare_job(
        backend_config=backend_config,
        project_dir=project_dir,
        project=project,
        entry_point=entry_point,
        parameters=parameters,
        run_id=run_id,
    )
    submitted = submitted_run.SubmittedUnicoreRun(run_id=run_id, job=job)

    logger.info(f"Submitted run {submitted}")
    return submitted


def _prepare_job(
    backend_config: t.Dict,
    project_dir: pathlib.Path,
    project: _project_spec.Project,
    entry_point: str,
    parameters: t.Dict,
    run_id: str,
) -> job_wrapper.Job:
    config = core.Config.from_dict(backend_config)

    files_to_upload = upload.get_files_to_upload(
        project_dir=project_dir, config=config
    )
    logger.debug(f"Prepared upload of files {files_to_upload}")

    client = _connect.create_unicore_api_connection(
        api_url=config.api_url,
        user=config.user,
        password=config.password,
    )
    client = client_wrapper.Client(client)
    entry = project.get_entry_point(entry_point)
    storage_dir = backend_config[projects.PROJECT_STORAGE_DIR]
    logger.debug(f"Writing to storage directory {storage_dir}")
    job = _submit_job_in_staging_in_and_upload_input_files(
        client=client,
        entry_point=entry,
        parameters=parameters,
        storage_dir=storage_dir,
        input_files=files_to_upload,
        config=config,
        run_id=run_id,
    )
    logger.debug(f"Submitted job {job.id} to staging in")
    return job


def _submit_job_in_staging_in_and_upload_input_files(
    client: client_wrapper.Client,
    entry_point: _project_spec.EntryPoint,
    parameters: t.Dict,
    storage_dir: str,
    input_files: t.List[pathlib.Path],
    config: core.Config,
    run_id: str,
) -> job_wrapper.Job:
    config.add_env_vars({"MLFLOW_RUN_ID": run_id})
    job_description = create_job_description(
        entry_point=entry_point,
        parameters=parameters,
        storage_dir=storage_dir,
        config=config,
    )

    logger.debug(f"Created job description {job_description}")

    job = client.submit_job(
        job_description=job_description, input_files=input_files, run_id=run_id
    )
    return job


def create_job_description(
    config: core.Config,
    entry_point: _project_spec.EntryPoint,
    parameters: t.Dict,
    storage_dir: str,
) -> t.Dict:
    logger.debug(
        "Using entry point (name: %s, parameters: %s, command: %s) to create "
        "job description",
        entry_point.name,
        entry_point.parameters,
        entry_point.command,
    )

    arguments = _create_arguments(
        entry_point=entry_point, parameters=parameters, storage_dir=storage_dir
    )

    logger.debug("Entry point converted to %s", arguments)

    if not arguments:
        raise ValueError(
            "Empty MLflow entry point command for entry point "
            f"{entry_point.name!r}"
        )

    job_description = config.to_job_description(arguments)

    logger.debug("Job description is %s", job_description)

    return job_description


def _create_arguments(
    entry_point: _project_spec.EntryPoint, parameters: t.Dict, storage_dir: str
) -> t.List[str]:
    command_string = entry_point.compute_command(
        user_parameters=parameters,
        storage_dir=storage_dir,
    )
    return command_string.replace(" \\\n ", "").replace("\n", "").split(" ")
