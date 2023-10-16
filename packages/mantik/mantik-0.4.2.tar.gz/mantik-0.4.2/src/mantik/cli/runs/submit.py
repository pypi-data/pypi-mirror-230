import argparse
import ast
import logging
import pathlib
import typing as t
import uuid

import click

import mantik
import mantik.cli._options as _main_options
import mantik.cli.runs._options as _options
import mantik.cli.runs.runs as runs
import mantik.utils as utils


logger = logging.getLogger(__name__)


@runs.cli.command("submit")
@click.argument(
    "mlproject-path",
    type=click.Path(exists=True, file_okay=False, path_type=pathlib.Path),
    required=True,
)
@click.option(
    "--run-name",
    default=None,
    type=str,
    help="Name of the Run.",
    required=True,
)
@click.option(
    "--experiment-id",
    default=None,
    type=int,
    help=f"""Experiment ID on MLflow.

        If not specified, it is inferred from the environment variable
        {utils.mlflow.EXPERIMENT_ID_ENV_VAR}.

    """,
)
@click.option(
    "--entry-point",
    required=False,
    default="main",
    show_default=True,
    help="Entrypoint of the MLproject file.",
)
@click.option(
    "--backend-config",
    type=click.Path(dir_okay=False, path_type=pathlib.Path),
    required=True,
    help="Relative path to backend config file.",
)
@click.option(
    "--parameter", "-P", show_default=True, default=lambda: [], multiple=True
)
@_main_options.VERBOSE
@_options.UNICORE_CONNECTION_ID
def run_project(
    run_name: str,
    mlproject_path: pathlib.Path,
    experiment_id: int,
    entry_point: str,
    backend_config: pathlib.Path,
    parameter: t.List[str],
    verbose: bool,  # noqa
    connection_id: t.Optional[uuid.UUID],
) -> None:
    """Submit an MLflow project as a run to the Mantik Compute Backend.

    `MLPROJECT_PATH` is the path to the MLflow project folder.

    """
    if experiment_id is None:
        experiment_id = utils.env.get_required_env_var(
            utils.mlflow.EXPERIMENT_ID_ENV_VAR
        )
    logger.debug("Initializing Compute Backend Client")
    client = mantik.ComputeBackendClient.from_env(connection_id=connection_id)
    logger.debug("Parsing MLflow entry point parameters")
    parameters = _dict_from_list(parameter)
    logger.debug("Submitting run to Compute Backend")
    response = client.submit_run(
        run_name=run_name,
        experiment_id=experiment_id,
        mlflow_parameters=parameters,
        backend_config=backend_config,
        mlproject_path=mlproject_path,
        entry_point=entry_point,
    )

    click.echo(response.content)


def _dict_from_list(parameters: t.List[str]) -> t.Dict:
    return dict([_parse_parameter_from_string(p) for p in parameters])


def _parse_parameter_from_string(parameter: str) -> t.Tuple[str, t.Any]:
    key, value = parameter.split("=", 1)
    return key, _parse_value(value)


def _parse_value(value: t.Any) -> t.Any:
    try:
        return ast.literal_eval(value)
    except (ValueError, SyntaxError):
        # If value is a string, `astr.literal_eval` raises ValueError
        # and in some cases a SyntaxError.
        try:
            return ast.literal_eval(f"'{value}'")
        except (ValueError, SyntaxError):
            raise argparse.ArgumentTypeError(f"Unable to parse {value}")
