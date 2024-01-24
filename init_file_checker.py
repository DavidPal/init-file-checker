#!/usr/bin/env python

"""Checker of __init__.py files.

Author: David Pal <davidko.pal@gmail.com>
Date: 2024

Usage:

   python init_file_checker.py [OPTIONS] [FILES ...]
"""

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
        description="Checker of __init__.py files in Python projects",
        allow_abbrev=False,
        add_help=True,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--add-missing",
        help="Add missing __init__.py files.",
        required=False,
        action="store_true",
        default=False,
    )
    parser.add_argument(
        "input_directories", help="List of directories", nargs="+", default=[], type=str
    )
    parsed_arguments = parser.parse_args()
    return parsed_arguments


def find_all_python_files_recursively(path: str) -> List[str]:
    """Finds all *.py files in directories recursively."""
    if pathlib.Path(path).is_file() and path.endswith(".py"):
        return [path]

    if pathlib.Path(path).is_dir():
        return [
            expanded_file_name
            for inner_file in sorted(pathlib.Path(path).iterdir())
            for expanded_file_name in find_all_python_files_recursively(str(inner_file))
        ]

    return []


def parent_directories(file_name: str, base_directory: str) -> List[str]:
    """List parent directories of file starting with a base directory."""
    parts = file_name.split("/")
    directories = []
    for i in range(len(parts)):
        directory = "/".join(parts[:i])
        if directory.startswith(base_directory):
            directories.append(directory)
    return directories


def find_all_subdirectories(file_names: List[str], base_directory: str) -> Set[str]:
    """Finds missing '__init__.py' files."""
    return {
        directory
        for file_name in file_names
        for directory in parent_directories(file_name, base_directory)
    }


def find_missing_init_files(directories: Iterable[str]) -> List[str]:
    """Finds missing '__init__.py' files in a list of directories."""
    missing_files = []
    for directory in directories:
        init_file_name = directory + "/" + "__init__.py"
        if not pathlib.Path(init_file_name).is_file():
            missing_files.append(init_file_name)
    return missing_files


def create_missing_init_files(file_names: List[str]):
    """Creates missing '__init__.py' files."""
    for file_name in file_names:
        pathlib.Path(file_name).touch()


def main():
    """Finds missing '__init__.py' files and, optionally, adds the missing files."""
    parsed_arguments = parse_command_line()

    # Find directories containing *.py files.
    directories_to_check: Set[str] = set()
    for input_directory in parsed_arguments.input_directories:
        # Resolve full path of each directory.
        base_directory = str(pathlib.Path(input_directory).resolve())
        if not pathlib.Path(base_directory).is_dir():
            die(2, f"'{input_directory}' is not a directory.")

        python_files = find_all_python_files_recursively(base_directory)
        subdirectories = find_all_subdirectories(python_files, base_directory)
        directories_to_check.update(subdirectories)

    # Find the list of missing __init__.py files.
    missing_files = find_missing_init_files(directories_to_check)

    # Report errors and exit.
    if missing_files and not parsed_arguments.add_missing:
        for file_name in missing_files:
            print(f"Missing file '{file_name}'.")
        die(1)

    # Create missing files.
    if parsed_arguments.add_missing:
        create_missing_init_files(missing_files)


if __name__ == "__main__":
    main()
