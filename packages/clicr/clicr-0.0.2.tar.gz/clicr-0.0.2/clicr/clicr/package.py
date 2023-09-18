from pathlib import Path

from rich import print
import typer

app = typer.Typer(add_completion=False)

@app.callback(invoke_without_command=True)
def callback():
    """
    Not yet implemented
    """
    raise NotImplementedError("To be available in a later version")
