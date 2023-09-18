import os

from typing import Optional

from discordcache import __appname__, __version__

import typer

from rich.console import Console

app = typer.Typer()

def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"{__appname__} version {__version__}")
        raise typer.Exit()
    
def _build_callback(value: bool) -> None:
    if value:
        os.system("python3 setup.py sdist bdist_wheel")
        raise typer.Exit()
    
@app.command()
def main(
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        "-v",
        help="Shows the current version of Merl",
        callback=_version_callback,
        is_eager=True,
    )
) -> None:
    return

@app.command()
def build(
    build: Optional[bool] = typer.Option(
        None,
        "--build",
        "-b",
        help="Builds the package",
        callback=_build_callback,
        is_eager=True,
    )
) -> None:
    return
