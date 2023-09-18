from typing import Optional

from rich import print
import typer

from .. import __version__

app = typer.Typer(
    add_completion=False,
    no_args_is_help=True,
    rich_markup_mode="rich",
    context_settings={
        'help_option_names': ['-h', '--help']
    }
)

def version(v:bool):
    if v:
        print(f"[bold green]$name[/bold green] {__version__}")
        raise typer.Exit()

@app.callback()
def callback(
    version: Optional[bool] = typer.Option(
        None, '-v', '--version', help="Shows $name version",
        is_eager=True, callback=version
    )
):
    """
    $description
    """

if __name__ == "__main__":
    app()
