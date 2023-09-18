from pathlib import Path
from configparser import ConfigParser

search = lambda x, y: [z for z in x if y in z][0]
pwd = Path().resolve()
pkg_path = Path(__file__).parent.resolve()

def author_format(name=None, email=None):
    gitconfig = ConfigParser()
    gitconfig.read(Path.home() / '.gitconfig')
    parts = [name, email]
    labels = ['name', 'email']
    for i in range(len(parts)):
        if parts[i] is None:
            try:
                parts[i] = gitconfig.get('user', labels[i])
            except FileNotFoundError:
                raise OSError(
                    f'Author {labels[i]} is not supplied through init,' +\
                    'and git is not found in your system.'
                )
            if parts[i] == '': 
                raise NameError(
                    f'Author {labels[i]} is not supplied through init, ' +\
                    f'and user.{labels[i]} is not found in git.\n' +\
                    f'Remove the need to set the --author-{labels[i]} ' +\
                    'parameters by setting your git config globals with ' +\
                    f'"git config user.{labels[i]} <{labels[i]}>".'
                )
    name, email = parts
    return f"{name} <{email}>"
