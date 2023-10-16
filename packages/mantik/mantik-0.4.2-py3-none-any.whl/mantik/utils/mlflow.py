"""MLflow-related util functions.

This source file contains code from [MLflow](https://github.com/mlflow/mlflow)
licensed under Apache-2.0 license, see
[here](https://github.com/mlflow/mlflow/blob/1eef4641df6f605b7d9faa83b0fc25e65877dbf4/LICENSE.txt)  # noqa: E501
for the original license.

Changes made to the original source code are denoted as such with comments.
"""
import mlflow.projects.utils as utils
import mlflow.tracking as tracking
import mlflow.tracking._tracking_service.utils as mlflow_utils
import mlflow.tracking.fluent as fluent
import mlflow.utils.mlflow_tags as mlflow_tags

import mantik.utils.env as env

TRACKING_URI_ENV_VAR = mlflow_utils._TRACKING_URI_ENV_VAR
TRACKING_TOKEN_ENV_VAR = mlflow_utils._TRACKING_TOKEN_ENV_VAR
TRACKING_USERNAME_ENV_VAR = mlflow_utils._TRACKING_USERNAME_ENV_VAR
TRACKING_PASSWORD_ENV_VAR = mlflow_utils._TRACKING_PASSWORD_ENV_VAR
EXPERIMENT_NAME_ENV_VAR = tracking._EXPERIMENT_NAME_ENV_VAR
EXPERIMENT_ID_ENV_VAR = tracking._EXPERIMENT_ID_ENV_VAR
RUN_NAME_ENV_VAR = "RUN_NAME"

CONFLICTING_ENV_VARS = (
    TRACKING_USERNAME_ENV_VAR,
    TRACKING_PASSWORD_ENV_VAR,
)


def unset_conflicting_env_vars() -> None:
    env.unset_env_vars(CONFLICTING_ENV_VARS)


def create_run(
    run_name, uri, experiment_id, work_dir, version, entry_point, parameters
):
    """
    This function is needed cause Mlflow, as of now (2.2.2),
    does not allow to pass a run name or set the run name tag
    when using get_or_create_run or _create_run
    from [the mlflow.projects.utils module](https://github.com/mlflow/mlflow/blob/977f794103977018d156b48833095e037208c718/mlflow/projects/utils.py#L263).  # noqa: E501

    As soon as this is possible with mlflow, this function can be deleted.
    """
    if utils._is_local_uri(uri):
        source_name = tracking._tracking_service.utils._get_git_url_if_present(
            utils._expand_uri(uri)
        )
    else:
        source_name = utils._expand_uri(uri)
    source_version = utils.get_git_commit(work_dir)
    existing_run = fluent.active_run()
    if existing_run:
        parent_run_id = existing_run.info.run_id
    else:
        parent_run_id = None

    tags = {
        mlflow_tags.MLFLOW_USER: utils._get_user(),
        mlflow_tags.MLFLOW_SOURCE_NAME: source_name,
        mlflow_tags.MLFLOW_SOURCE_TYPE: utils.SourceType.to_string(
            utils.SourceType.PROJECT
        ),
        mlflow_tags.MLFLOW_PROJECT_ENTRY_POINT: entry_point,
    }
    if source_version is not None:
        tags[mlflow_tags.MLFLOW_GIT_COMMIT] = source_version
    if parent_run_id is not None:
        tags[mlflow_tags.MLFLOW_PARENT_RUN_ID] = parent_run_id

    repo_url = utils.get_git_repo_url(work_dir)
    if repo_url is not None:
        tags[mlflow_tags.MLFLOW_GIT_REPO_URL] = repo_url
        tags[mlflow_tags.LEGACY_MLFLOW_GIT_REPO_URL] = repo_url

    # Add branch name tag if a branch is specified through -version
    if utils._is_valid_branch_name(work_dir, version):
        tags[mlflow_tags.MLFLOW_GIT_BRANCH] = version
        tags[mlflow_tags.LEGACY_MLFLOW_GIT_BRANCH_NAME] = version
    active_run = tracking.MlflowClient().create_run(
        #
        # MODIFIED: `run_name` passed
        #
        experiment_id=experiment_id,
        tags=tags,
        run_name=run_name,
    )

    project = utils._project_spec.load_project(work_dir)
    # Consolidate parameters for logging.
    # `storage_dir` is `None`
    # since we want to log actual path not downloaded local path
    entry_point_obj = project.get_entry_point(entry_point)
    final_params, extra_params = entry_point_obj.compute_parameters(
        parameters, storage_dir=None
    )
    params_list = [
        utils.Param(key, value)
        for key, value in list(final_params.items())
        + list(extra_params.items())
    ]
    tracking.MlflowClient().log_batch(
        active_run.info.run_id, params=params_list
    )
    return active_run
