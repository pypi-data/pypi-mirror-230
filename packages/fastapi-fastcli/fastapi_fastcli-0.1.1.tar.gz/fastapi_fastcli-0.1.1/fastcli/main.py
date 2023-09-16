import os
import sys
from typing import Optional

import typer
import uvicorn
from rich.console import Console
from rich.table import Table
from typing_extensions import Annotated

from . import __version__
from .utils import load_fastapi_app, load_typer_app

sys.path.append(os.getcwd())

console = Console()
app = load_typer_app()


def version_callback(value: bool):
    if value:
        print(f"FastAPI CLI Version: {__version__}")
        raise typer.Exit()


@app.callback()
def callback(
    version: Annotated[
        Optional[bool],
        typer.Option(
            "--version",
            callback=version_callback,
            is_eager=True,
            help="Show version and exit.",
        ),
    ] = None
):
    """
    FastAPI Command line interface
    """
    pass


@app.command(help="Start server")
def run(
    app: Annotated[
        str, typer.Option("--app", "-A", envvar="FASTAPI_APP", help="Application")
    ] = "main:app",
    host: Annotated[str, typer.Option("--host", "-H", help="Host")] = "127.0.0.1",
    port: Annotated[int, typer.Option("--port", "-P", help="Port")] = 8000,
    reload: Annotated[bool, typer.Option(is_flag=True, help="Reload")] = False,
):
    uvicorn.run(app=app, host=host, port=port, reload=reload)


@app.command(help="Display routes")
def routes(
    app: Annotated[
        str, typer.Option("--app", "-A", envvar="FASTAPI_APP", help="Application")
    ] = "main:app"
):
    fastapp = load_fastapi_app(app)
    routes = sorted(fastapp.routes, key=lambda x: x.path)  # type: ignore
    table = Table("Path", "Name", "Methods")
    for route in routes:
        table.add_row(route.path, route.name, ", ".join(route.methods))  # type: ignore
    console.print(table)
