import pathlib
import typing as t
import uuid

import click

import mantik.cli.runs._arguments as _arguments
import mantik.cli.runs._options as _options
import mantik.cli.runs.runs as runs
import mantik.unicore as unicore


@runs.cli.command("info")
@_arguments.JOB_ID
@_options.API_URL
@_options.BACKEND_CONFIG_ABSOLUTE
@_options.UNICORE_CONNECTION_ID
@click.option(
    "-f",
    "--format",
    "fmt",
    type=click.Choice(["JSON", "YAML"], case_sensitive=False),
    required=False,
    default="YAML",
    show_default=True,
    help="Output format.",
)
def print_info(
    job_id: str,
    api_url: t.Optional[str],
    backend_config: t.Optional[pathlib.Path],
    fmt: t.Optional[str],
    connection_id: t.Optional[uuid.UUID],
) -> None:
    """Print detailed run info.

    JOB_ID is the job ID assigned by UNICORE.

    """
    client = unicore.client.Client.from_api_url_or_config(
        api_url=api_url, config=backend_config, connection_id=connection_id
    )
    job = client.get_job(job_id)
    click.echo(_format_job(job, fmt=fmt))


def _format_job(job: unicore.job.Job, fmt: str) -> str:
    if fmt == "JSON":
        return job.to_json()
    elif fmt == "YAML":
        return job.to_yaml()
    click.BadParameter(f"Format {fmt} not supported")
