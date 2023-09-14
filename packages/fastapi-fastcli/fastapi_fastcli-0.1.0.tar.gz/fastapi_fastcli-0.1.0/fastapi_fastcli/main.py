from typing import Annotated

import typer

from . import __version__

app = typer.Typer()
config_app = typer.Typer(help="Config Management")
app.add_typer(config_app, name="config")


@app.callback()
def callback():
    """
    Fastapi command line tool
    """


@app.command()
def version():
    """
    Display Version
    """
    typer.echo(__version__)


@config_app.command()
def set(
    name: Annotated[str, typer.Option(help="Option name")],
    value: Annotated[str, typer.Option(help="Option value")],
):
    """
    Set config
    """
    typer.echo(f"{name}={value}")
