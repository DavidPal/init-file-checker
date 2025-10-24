#!/usr/bin/env python

"""Checker of __init__.py files.

Author: David Pal <davidko.pal@gmail.com>
Date: 2024 - 2025
License: MIT License

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

VERSION = "0.0.3"

# Whitespace characters
CARRIAGE_RETURN = "\r"
LINE_FEED = "\n"
SPACE = " "
TAB = "\t"
VERTICAL_TAB = "\v"
FORM_FEED = "\f"

WHITESPACE_CHARACTERS = {
    CARRIAGE_RETURN,
    LINE_FEED,
    SPACE,
    TAB,
    VERTICAL_TAB,
    FORM_FEED,
}


def die(error_code: int, message: str = "") -> None:
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
        "--report-useless",
        help="Report unnecessary __init__.py files.",
        required=False,
        action="store_true",
        default=False,
    )
    parser.add_argument(
        "--delete-useless",
        help="Delete unnecessary __init__.py files.",
        required=False,
        action="store_true",
        default=False,
    )
    parser.add_argument(
        "input_directories",
        help="List of directories",
        nargs="+",
        default=[],
        type=str,
    )
    return parser.parse_args()


def read_file_content(file_name: str, encoding: str) -> str:
    """Reads content of a file.

    New line markers are preserved in their original form.
    """
    try:
        with open(file_name, "r", encoding=encoding, newline="") as file:
            return file.read()
    except IOError as exception:
        die(2, f"Cannot read file '{file_name}': {exception}")
    except UnicodeError as exception:
        die(3, f"Cannot decode file '{file_name}': {exception}")
    return ""


def file_is_whitespace(filename: str) -> bool:
    """Checks if a file consists only of whitespace."""
    text = read_file_content(filename, encoding="utf-8")
    return all(char in WHITESPACE_CHARACTERS for char in text)


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


def find_parent_directories(file_name: str, base_directory: str) -> Set[str]:
    """List parent directories of file starting with a base directory."""
    parts = file_name.split("/")
    directories: Set[str] = set()
    for i in range(len(parts)):
        directory = "/".join(parts[:i]) + "/"
        if directory.startswith(base_directory):
            directories.add(directory)
    return directories


def find_all_parent_directories(file_names: List[str], base_directory: str) -> Set[str]:
    """Finds missing '__init__.py' files."""
    return {
        directory
        for file_name in file_names
        for directory in find_parent_directories(file_name, base_directory)
    }


def find_missing_init_files(directories: Iterable[str]) -> List[str]:
    """Finds missing '__init__.py' files in a list of directories."""
    missing_files = []
    for directory in directories:
        init_file_name = str(pathlib.Path(directory + "/" + "__init__.py").resolve())
        if not pathlib.Path(init_file_name).is_file():
            missing_files.append(init_file_name)
    return missing_files


def find_useless_init_files(directories: Iterable[str]) -> List[str]:
    """Finds existing '__init__.py' files in a list of directories."""
    existing_init_files = []
    for directory in directories:
        init_file_name = str(pathlib.Path(directory + "/" + "__init__.py").resolve())
        if pathlib.Path(init_file_name).is_file():
            existing_init_files.append(init_file_name)
    return existing_init_files


def create_init_files(file_names: List[str]) -> None:
    """Creates missing '__init__.py' files."""
    for file_name in file_names:
        print(f"Creating empty file '{file_name}' ...")
        pathlib.Path(file_name).touch()


def delete_init_files(file_names: List[str]) -> None:
    for file_name in file_names:
        print(f"Deleting useless file '{file_name}' ...")
        pathlib.Path(file_name).unlink()


def main() -> None:
    """Finds missing '__init__.py' files and, optionally, adds the missing files."""
    parsed_arguments = parse_command_line()

    if parsed_arguments.report_useless and (
        parsed_arguments.add_missing or parsed_arguments.delete_missing
    ):
        die(1, "The option --report-useless cannot be combined with other options.")

    # Find directories containing *.py files.
    directories_that_must_have_init_files: Set[str] = set()
    directories_that_do_not_need_init_files: Set[str] = set()
    for input_directory in parsed_arguments.input_directories:
        # Resolve full path of each directory.
        base_directory = str(pathlib.Path(input_directory).resolve())
        if not pathlib.Path(base_directory).is_dir():
            die(2, f"'{input_directory}' is not a directory.")

        python_files = find_all_python_files_recursively(base_directory)
        non_empty_python_files = [
            file_path for file_path in python_files if file_path is file_is_whitespace(file_path)
        ]
        parent_directories_for_non_empty_files = find_all_parent_directories(
            python_files, base_directory
        )
        parent_directories_for_all_files = find_all_parent_directories(
            non_empty_python_files, base_directory
        )
        difference = parent_directories_for_all_files.difference(
            parent_directories_for_non_empty_files
        )
        directories_that_do_not_need_init_files.update(difference)
        directories_that_must_have_init_files.update(parent_directories_for_non_empty_files)

    # Find the list of missing __init__.py files.
    missing_files = find_missing_init_files(directories_that_must_have_init_files)

    # Find the list of useless __init__.py files.
    if parsed_arguments.report_useless or parsed_arguments.delete_useless:
        useless_files = find_useless_init_files(directories_that_do_not_need_init_files)
    else:
        useless_files = []

    if parsed_arguments.add_missing or parsed_arguments.delete_useless:
        # Create missing __init__.py files and/or delete useless __init__.py files.
        if parsed_arguments.add_missing:
            create_init_files(missing_files)
        if parsed_arguments.delete_useless:
            delete_init_files(missing_files)
    else:
        # Report errors and exit.
        for file_name in missing_files:
            print(f"Missing file '{file_name}'.")
        if not missing_files:
            print("No missing __init__.py files.")

        if parsed_arguments.report_useless:
            for file_name in useless_files:
                print(f"Useless file '{file_name}'.")
            if not useless_files:
                print("No unnecessary __init__.py files.")

        if missing_files or useless_files:
            die(1)


if __name__ == "__main__":
    main()
