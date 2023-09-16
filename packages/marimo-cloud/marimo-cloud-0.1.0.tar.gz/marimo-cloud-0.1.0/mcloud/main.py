import typer

import mcloud.auth as marimo_auth
import mcloud.publish as marimo_publish
from rich.console import Console

console = Console()
app = typer.Typer(
    pretty_exceptions_show_locals=False,
    pretty_exceptions_short=True,
)

__version__ = "0.1.0"

@app.command()
def version():
    console.print(__version__)

@app.command()
def login():
    marimo_auth.login()

@app.command()
def publish():
    marimo_publish.publish()

@app.command()
def logout():
    marimo_auth.logout()

if __name__ == "__main__":
    app()
