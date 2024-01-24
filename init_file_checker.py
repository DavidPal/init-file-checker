#!/usr/bin/env python

"""TODO: Add docstring."""

from __future__ import annotations

import argparse
import pathlib
import sys
from typing import Iterable
from typing import List
from typing import Set

VERSION = "0.0.1"


def die(error_code: int, message: str = ""):
    """Exits the script."""
    if message:
        print(message)
    sys.exit(error_code)


def parse_command_line() -> argparse.Namespace:
    """Parses command line arguments."""
    parser = argparse.ArgumentParser(
        prog="init-file-checker",
        description="Linter and formatter for source code files and text files",
        allow_abbrev=False,
        add_help=True,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--add-missing",
        help="Do not format files. Only report which files would be formatted.",
        required=False,
        action="store_true",
        default=False,
    )
    parser.add_argument("input_files", help="List of input files", nargs="+", default=[], type=str)
    parsed_arguments = parser.parse_args()
    return parsed_arguments


def find_all_python_files_recursively(file_name: str) -> List[str]:
    """Finds all *.py files in directories recursively."""
    if pathlib.Path(file_name).is_file() and file_name.endswith(".py"):
        return [file_name]

    if pathlib.Path(file_name).is_dir():
        return [
            expanded_file_name
            for inner_file in sorted(pathlib.Path(file_name).iterdir())
            for expanded_file_name in find_all_python_files_recursively(str(inner_file))
        ]

    return []


def find_all_python_files(file_names: List[str]) -> List[str]:
    """Finds all *.py files in directories recursively."""
    return [
        expanded_file_name
        for file_name in file_names
        for expanded_file_name in find_all_python_files_recursively(file_name)
    ]


def parent_directories(file_name: str) -> List[str]:
    """List parent directories of a relative or absolute path of a file."""
    parts = file_name.split("/")
    root_prefix = "/" if file_name.startswith("/") else ""
    return [
        root_prefix + "/".join(parts[:i])
        for i in range(len(parts))
    ]


def find_all_directories(file_names: List[str]) -> Set[str]:
    """Finds missing '__init__.py' files."""
    return {
        directory
        for file_name in file_names
        for directory in parent_directories(file_name)
    }


def find_missing_init_files(directories: Iterable[str]) -> List[str]:
    """Finds missing '__init__.py' files in a list of directories."""
    missing_files = []
    for directory in directories:
        if not directory:
            init_file_name = "__init__.py"
        else:
            init_file_name = directory + "/" + "__init__.py"
        if not pathlib.Path(init_file_name).is_file():
            print(f"Missing file '{init_file_name}'.")
            missing_files.append(init_file_name)
    return missing_files


def create_missing_init_files(file_names: List[str]):
    """Creates missing '__init__.py' files."""
    for file_name in file_names:
        pathlib.Path(file_name).touch()


def main():
    """Finds missing '__init__.py' files and, optionally, adds the missing files."""
    parsed_arguments = parse_command_line()
    file_names = find_all_python_files(parsed_arguments.input_files)
    directories = find_all_directories(file_names)
    print(directories)
    missing_files = find_missing_init_files(directories)
    if missing_files and not parsed_arguments.add_missing:
        die(1)
    if parsed_arguments.add_missing:
        create_missing_init_files(missing_files)


if __name__ == "__main__":
    main()
