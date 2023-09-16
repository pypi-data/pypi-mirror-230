import rich
import typer

from radops import __version__

from .config import app as config_app
from .data_lake import app as datalake_app
from .jobs import app as jobs_app

app = typer.Typer()
app.add_typer(datalake_app, name="datalake")
app.add_typer(config_app, name="config")
app.add_typer(jobs_app, name="executors")


def version_callback(value):
    if value:
        rich.print(__version__)
        raise typer.Exit()


@app.callback()
def common(
    version: bool = typer.Option(None, "--version", callback=version_callback),
):
    pass


if __name__ == "__main__":
    app()
