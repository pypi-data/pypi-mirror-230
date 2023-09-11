# imports
import os
import sys
import toml
import typer


from dotenv import load_dotenv
from typing_extensions import Annotated

# local imports
# load .env file
load_dotenv()
load_dotenv(os.path.expanduser("~/.dkdc/.env"))

# load config
try:
    config = toml.load(os.path.expanduser("~/.dkdc/config.toml"))
except FileNotFoundError:
    config = {}

# typer config
app = typer.Typer(no_args_is_help=True)

from netsky.testing import testing_run

# global options
def version(value: bool):
    if value:
        version = toml.load("pyproject.toml")["project"]["version"]
        typer.echo(f"{version}")
        raise typer.Exit()


# subcommands
@app.command()
def test():
    """
    test
    """
    testing_run()


# main
@app.callback()
def cli(
    version: bool = typer.Option(
        None, "--version", help="Show version.", callback=version, is_eager=True
    ),
):
    version = version
    # Do other global stuff, handle other global options here
    return


## main
if __name__ == "__main__":
    typer.run(cli)
