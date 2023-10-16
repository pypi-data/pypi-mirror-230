import mantik.cli.main as main


@main.cli.group("runs")
def cli() -> None:
    """Interaction with Mantik runs."""
