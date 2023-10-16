import click

import mantik.cli.main as main
import mantik.tracking.track as track


@main.cli.command("init")
@click.option(
    "--no-export",
    is_flag=True,
    show_default=True,
    default=False,
    help="Strip the `export` prefix of the output.",
)
def initialize_tracking(no_export: bool) -> None:
    """Initialize the authentication to mantik and
    print the required environment variables.

    It is not possible to set environment variables in a parent process
    (or shell) from a subprocess (e.g. Python). Thus, the `init` command prints
    the bash export statement with the required environment variable for
    authentication to mantik.
    As a consequence, the output can be directly used to set
    the environment variable in the parent process by using the `eval` bash
    command:

    \b
    ```shell
    eval $(mantik init)
    ```

    If you do not want to set the environment variable in the parent process
    but only want to pass it to the command context, use the `env` bash command
    combined with the `--no-export` flag:

    \b
    ```shell
    env $(mantik init --no-export) <command>
    ```

    """
    environment = track.init_tracking()

    click.echo(environment.to_bash_statement(no_export=no_export))
