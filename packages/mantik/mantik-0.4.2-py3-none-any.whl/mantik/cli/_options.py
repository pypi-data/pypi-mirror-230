import click

import mantik.cli._callbacks as _callbacks


VERBOSE = click.option(
    "--verbose",
    "-v",
    is_flag=True,
    callback=_callbacks.set_verbose_logging,
    help="Set logging to verbose mode.",
)
