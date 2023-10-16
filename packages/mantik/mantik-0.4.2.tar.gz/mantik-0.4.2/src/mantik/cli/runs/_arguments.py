import click

JOB_ID = click.argument(
    "job-id",
    type=str,
    required=True,
)
