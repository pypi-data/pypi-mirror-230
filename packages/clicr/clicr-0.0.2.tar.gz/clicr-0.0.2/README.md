# `clicr`, the CLI Creator

`clicr` (pronounced as *clicker*) is the CLI Creator that aims to be 
the template used to make effective CLI apps using Python.

## Getting Started (Development)

Install [Poetry][poetry]:

[poetry]: https://python-poetry.org/docs/#installing-with-the-official-installer

```bash
curl -sSL https://install.python-poetry.org | python3 -
```

Create new environment, or use existing environment:

```bash
# Change your python version accordingly (>=3.8)
conda create -n clicr python
conda activate clicr
```

Then install the dependencies in Poetry:

```python
poetry install
```

You can now use the `clicr` in the CLI.
Check `clicr --help` for more information.

To run the documentation, run `mkdocs server` and check out the site at
`localhost:8000`.

## Template Stack
- Typer
- Poetry

## Development Stack
- Scriv
- MkDocs

## Managing Changelog

This repository's changelog is managed by [Scriv].

[Scriv]: https://github.com/nedbat/scriv

## License

© Copyright 2022 Syakyr Surani.
This program is licensed under [Apache Software License 2.0](LICENSE).

