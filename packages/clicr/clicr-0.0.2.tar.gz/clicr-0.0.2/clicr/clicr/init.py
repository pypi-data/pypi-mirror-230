from pathlib import Path
from string import Template
from typing import Optional

from rich import print
import typer

from ..utils import pwd, pkg_path, search, author_format

app = typer.Typer(add_completion=False)

tpl_path = pkg_path / 'init_template'

def src_name():
    """
    Check if src folder exists, otherwise use the name of the folder
    instead, since those two names are the standard for source code
    files
    """
    src = pwd / 'src'
    if src.exists() and src.is_dir():
        return 'src'
    else:
        return pwd.name.lower().replace(' ', '_').replace('-', '_')

@app.callback(invoke_without_command=True)
def callback(
    src_name: str = typer.Option(
        src_name(), 
        help="Name of source code directory"
    ),
    cli_name: str = typer.Option(
        pwd.name.lower().replace(' ', '-').replace('_', '-'),
        help="Name of CLI app"
    ),
    description: str = typer.Option(
        "A CLI app powered by clicr.",
        help="Description of the CLI app"
    ),
    author_name: str = typer.Option(
        None,
        help="Name of the CLI author"
    ),
    author_email: str = typer.Option(
        None,
        help="Email address of the CLI author"
    )
):
    """
    Creates a base [green]Clicr[/green] project
    """
    # Setting up checks:
    # - .clicr folder
    # - clicr folder in the src_name folder
    # - pyproject.toml
    # - README.md
    clicr_dir   = pwd / '.clicr'
    src_dir     = pwd / src_name
    clicr_src   = src_dir / 'clicr'
    toml_file   = pwd / 'pyproject.toml'
    readme_file = pwd / 'README.md'
    init = False

    ## .clicr folder
    # Nothing to add here for now, just an empty config file
    init_tpl_fdr = Path(__file__).parent / 'init_template'
    config_file  = clicr_dir / 'config'
    config_tpl   = init_tpl_fdr / 'config'
    if clicr_dir.exists():
        init = True
    else:
        clicr_dir.mkdir()
    if not config_file.exists():
        config_file.write_text(config_tpl.read_text())
    ## clicr folder
    # - Adds main.py into the clicr folder
    # - Appends __init__.py into the root src folder if __version__ 
    #   doesn't exist
    main_tpl     = init_tpl_fdr / 'main.py'
    main_file    = clicr_src / 'main.py'
    if clicr_src.exists():
        init = True
    else:
        clicr_src.mkdir(parents=True)
    if not main_file.exists():
        text = Template(main_tpl.read_text()).substitute(
            name=cli_name, description=description
        )
        main_file.write_text(text)
    init_tpl     = init_tpl_fdr / '__init__.py'
    init_file    = src_dir / '__init__.py'
    if init_file.exists():
        init_lines_cur = init_file.read_text()
        if '__version__' not in init_lines_cur:
            init_lines = init_tpl.read_text().split('\n')
            ipt = search(init_lines, 'importlib.metadata')
            ver = search(init_lines, '__version__')
            init_file.write_text(f"{ipt}\n{init_lines_cur}\n{ver}")
    else: init_file.write_text(init_tpl.read_text())
    ## pyproject.toml and README.md files
    # - Add the files into the root folder if it doesn't exist
    # - Add the files with _cli appended to the names if it does exist
    #   + TODO: Integrate the files into existing files
    toml_tpl   = init_tpl_fdr / f'pyproject.toml'
    readme_tpl = init_tpl_fdr / f'README.md'
    if toml_file.exists():
        toml_file = pwd / 'pyproject_cli.toml'
    text = Template(toml_tpl.read_text()).substitute(
        cliname=cli_name, srcname=src_name,
        author=author_format(author_name, author_email),
        description=description
    )
    toml_file.write_text(text)
    if readme_file.exists():
        readme_file = pwd / 'README_cli.md'
    text = Template(readme_tpl.read_text()).substitute(name=cli_name)
    readme_file.write_text(text)
    
    if init:
        print(f"Reinitialized base Clicr project in {pwd}.")
    else:
        print(f"Initialized base Clicr project in {pwd}.")

if __name__ == "__main__":
    app()
