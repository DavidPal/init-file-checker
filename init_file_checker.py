#!/usr/bin/env python

"""TODO: Add docstring."""

from __future__ import annotations

import argparse
import pathlib
from typing import List

VERSION = "0.0.1"


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


def find_all_files_recursively(file_name: str) -> List[str]:
    """Finds files in directories recursively."""
    if pathlib.Path(file_name).is_file() and file_name.endswith(".py"):
        return [file_name]

    if pathlib.Path(file_name).is_dir():
        return [
            expanded_file_name
            for inner_file in sorted(pathlib.Path(file_name).iterdir())
            for expanded_file_name in find_all_files_recursively(str(inner_file))
        ]

    return []


def find_files_to_process(file_names: List[str]) -> List[str]:
    """Finds files that need to be processed.

    The function excludes files that match the regular expression specified
    by the --exclude command line option.
    """
    return [
        expanded_file_name
        for file_name in file_names
        for expanded_file_name in find_all_files_recursively(file_name)
    ]


def main():
    """Finds missing __init__.py files."""
    parsed_arguments = parse_command_line()
    file_names = find_files_to_process(parsed_arguments.input_files)
    print(file_names)


if __name__ == "__main__":
    main()
