# `__init__` file checker

[![Build, lint and test](https://github.com/DavidPal/init-file-checker/actions/workflows/build.yaml/badge.svg)](https://github.com/DavidPal/init-file-checker/actions/workflows/build.yaml)

Tool that ensures that `__init__.py` files are not missing. Various Python tools needs these files, most notably pylint.

## Installation

```shell
pip install init-file-checker
```

Installation requires Python 3.8.5 or higher.

## Usage

A sample command that checks presence of `__init__.py` files is:
```shell
init-file-checker my_project/
```

If you want to create missing `__init__.py` files, use `--add-missing` command line option:
```shell
init-file-checker --add-missing my_project/
```
The created files will have zero size.

## License

MIT
