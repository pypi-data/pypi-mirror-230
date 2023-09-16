import importlib
import os

import typer
from fastapi import FastAPI
from rich import print

mapping = {"typer": typer.Typer, "fastapi": FastAPI}


def load_instance(app: str, instance_type: str) -> FastAPI:  # type: ignore
    try:
        module_name, app_name = app.split(":")
        module = importlib.import_module(module_name)
        return (  # type: ignore
            getattr(module, app_name)
            if hasattr(module, app_name)
            and isinstance(getattr(module, app_name), mapping[instance_type])
            else None
        )
    except ValueError:
        typer.echo("must be like 'main:app'")
        raise typer.Abort()
    except ModuleNotFoundError:
        pass


def load_typer_app() -> typer.Typer:
    app = typer.Typer()
    if os.environ.get("TYPER_APP"):
        app_path = [os.environ["TYPER_APP"]]
    else:
        app_path = [
            "app.commands:app",
            "app.cli:app",
            "cli:app",
            "main:cli",
            "manage:cli",
            "app:cli",
        ]
    for path in app_path:
        loaded_instance = load_instance(path, "typer")
        if loaded_instance:
            app = loaded_instance
            break
    if not any(
        [app.registered_callback, app.registered_commands, app.registered_groups]  # type: ignore
    ):
        print(
            "[bold red]The typer application was not found in the following default path. "
            "You can specify the location of the instance by setting the TYPER_APP environment variable " 
            "such as TYPER_APP=example.main:app[/bold red][yellow]\n  - {}[/yellow]".format(
                "\n  - ".join(app_path)
            )
        )
        typer.Exit(1)
    return app  # type: ignore


def load_fastapi_app(app: str) -> FastAPI:  # type: ignore
    loaded_instance = load_instance(app, "fastapi")
    if loaded_instance:
        return loaded_instance
