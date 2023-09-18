# `$name`, powered by `clicr`

`$name` has been`` created using `clicr`.

## Developing `$name`

Install [Poetry][poetry]:

[poetry]: https://python-poetry.org/docs/#installing-with-the-official-installer

```bash
curl -sSL https://install.python-poetry.org | python3 -
```

Create new environment, or use existing environment:

```bash
# Change your python version accordingly (>=3.8)
conda create -n $name python
conda activate $name
```

Then install the dependencies in Poetry:

```python
poetry install
```

You can now use the `$name` in the CLI.
Check `$name --help` for more information.

## Template Stack
- Typer
- Poetry
- Clicr

