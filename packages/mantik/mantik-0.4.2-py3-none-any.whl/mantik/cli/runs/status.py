import pathlib
import typing as t
import uuid

import click

import mantik.cli.runs._arguments as _arguments
import mantik.cli.runs._options as _options
import mantik.cli.runs.runs as runs
import mantik.unicore as unicore


@runs.cli.command("status")
@_arguments.JOB_ID
@_options.API_URL
@_options.BACKEND_CONFIG_ABSOLUTE
@_options.UNICORE_CONNECTION_ID
def print_status(
    job_id: str,
    api_url: t.Optional[str],
    backend_config: t.Optional[pathlib.Path],
    connection_id: t.Optional[uuid.UUID],
) -> None:
    """Print the run status.

    JOB_ID is the job ID assigned by UNICORE.

    """
    client = unicore.client.Client.from_api_url_or_config(
        api_url=api_url, config=backend_config, connection_id=connection_id
    )
    job = client.get_job(job_id)
    click.echo(job.status.value)
