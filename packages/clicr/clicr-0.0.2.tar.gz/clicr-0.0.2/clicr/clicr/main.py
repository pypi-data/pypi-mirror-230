from importlib import import_module
from pathlib import Path
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
cmd_list = [
    x.name.split('.')[0] for x in
    Path(__file__).parent.iterdir()
    if 'py' == x.name.split('.')[-1]
    and x.is_file()
]
cmd_list.remove('main')
short_cmds = {
    'package': ['pkg'],
    'template': ['tpl'],
    'command': ['cmd']
}
for cmd in cmd_list:
    try:
        pkg_app = import_module(f'.{cmd}', package=__package__).app
        app.add_typer(pkg_app, name=cmd)
        if cmd in short_cmds:
            for scmd in short_cmds[cmd]:
                app.add_typer(pkg_app, name=scmd, hidden=True)
    except:
        # Ignores if script doesn't have app function
        pass

def version(v:bool):
    if v:
        print(f"[bold green]clicr[/bold green] {__version__}")
        raise typer.Exit()

@app.callback()
def callback(
    version: Optional[bool] = typer.Option(
        None, '-v', '--version', help="Shows clicr version",
        is_eager=True, callback=version
    )
):
    """
    CLI Creator for Python
    """

if __name__ == "__main__":
    app()
