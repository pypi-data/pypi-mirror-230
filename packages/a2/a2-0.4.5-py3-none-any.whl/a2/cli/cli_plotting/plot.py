import a2.cli.main as main


@main.cli.group("plot")
def cli() -> None:
    """Plotting routines of a2."""
