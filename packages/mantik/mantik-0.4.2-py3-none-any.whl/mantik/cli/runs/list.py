import pathlib
import typing as t
import uuid

import click

import mantik.cli.runs._options as _options
import mantik.cli.runs.runs as runs
import mantik.unicore as unicore


@runs.cli.command("list")
@_options.API_URL
@_options.BACKEND_CONFIG_ABSOLUTE
@_options.UNICORE_CONNECTION_ID
@click.option(
    "-o",
    "--offset",
    type=int,
    required=False,
    default=0,
    help="Skip n jobs.",
)
@click.option(
    "-t",
    "--total",
    type=int,
    required=False,
    default=10,
    help="Maximum number of jobs to list.",
)
def print_info(
    api_url: str,
    backend_config: t.Optional[pathlib.Path],
    offset: t.Optional[int],
    total: t.Optional[int],
    connection_id: t.Optional[uuid.UUID],
) -> None:
    """Print all runs submitted to the remote system."""
    client = unicore.client.Client.from_api_url_or_config(
        api_url=api_url, config=backend_config, connection_id=connection_id
    )
    jobs = client.get_jobs(
        offset=offset,
        total=total,
    )
    rows = _format_rows(jobs)
    click.echo("\n".join(rows))


def _format_rows(jobs: t.List[unicore.job.Job]) -> t.List[str]:
    row_format = _get_row_format(jobs)
    return [
        *_format_header(row_format),
        *_format_jobs(jobs, row_format=row_format),
    ]


def _get_row_format(jobs):
    format_offset = 2
    id_length = _get_max_length(jobs, attribute="id", offset=format_offset)
    time_stamp_length = unicore.properties.TIMESTAMP_STR_LENGTH + format_offset
    queue_length = _get_max_length(
        jobs, attribute="queue", offset=format_offset
    )
    status_length = _get_max_length(
        jobs, attribute="status", offset=format_offset
    )
    return (
        f"{{job_id:{id_length}}}"
        f"{{submitted_at:{time_stamp_length}}}"
        f"{{queue:{queue_length}}}"
        f"{{status:{status_length}}}"
    )


def _format_header(row_format: str) -> t.List[str]:
    header = row_format.format(
        job_id="Job ID",
        submitted_at="Submitted At",
        queue="Queue",
        status="Status",
    )
    separator = "-" * len(header)
    return [header, separator]


def _format_jobs(jobs: t.List[unicore.job.Job], row_format: str) -> t.List[str]:
    return [
        row_format.format(
            job_id=job.id,
            submitted_at=job.submitted_at.strftime(
                unicore.properties.UNICORE_TIMESTAMP_FORMAT
            ),
            queue=job.queue,
            status=job.status.value,
        )
        for job in jobs
    ]


def _get_max_length(
    jobs: t.List[unicore.job.Job], attribute: str, offset: int = 2
) -> int:
    return max(len(getattr(job, attribute)) for job in jobs) + offset
