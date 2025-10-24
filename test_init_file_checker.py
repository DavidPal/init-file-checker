"""Unit tests for init_file_checker module."""

import pathlib
import re
import unittest
from typing import Optional

import init_file_checker

CURRENT_DIRECTORY_FULL_PATH = str(pathlib.Path(__file__).parent.resolve())


def extract_version_from_pyproject() -> Optional[str]:
    """Extracts version from pyproject.toml file."""
    with open("pyproject.toml", "r", encoding="utf-8") as file:
        lines = file.readlines()

    for line in lines:
        match = re.match(r"^version\s+=\s+\"(.*)\"$", line)
        if match:
            return match.group(1)

    return None


class TestInitFileChecker(unittest.TestCase):
    """Unit tests for init_file_checker module."""

    def test_check_version(self) -> None:
        """Verify that version numbers are the same in all places."""
        self.assertEqual(init_file_checker.VERSION, extract_version_from_pyproject())

    def test_dummy(self) -> None:
        """Tests equality of Lines."""
        self.assertEqual(2, 1 + 1)

    def test_find_parent_directories(self) -> None:
        """Test find_parent_directories() function."""
        self.assertSetEqual(
            {"/", "/path/", "/path/to/", "/path/to/some/"},
            init_file_checker.find_parent_directories("/path/to/some/file.txt", "/"),
        )
        self.assertSetEqual(
            {"/path/to/", "/path/to/some/"},
            init_file_checker.find_parent_directories("/path/to/some/file.txt", "/path/to"),
        )
        self.assertSetEqual(
            {"/path/to/", "/path/to/some/"},
            init_file_checker.find_parent_directories("/path/to/some/file.txt", "/path/to/"),
        )
        self.assertSetEqual(
            {"/path/to/some/"},
            init_file_checker.find_parent_directories("/path/to/some/file.txt", "/path/to/some"),
        )
        self.assertSetEqual(
            {"/path/to/some/"},
            init_file_checker.find_parent_directories("/path/to/some/file.txt", "/path/to/some/"),
        )

    def test_find_all_python_files_recursively(self) -> None:
        """Tests find_all_python_files_recursively() function."""
        self.assertEqual(
            [
                CURRENT_DIRECTORY_FULL_PATH + "/init_file_checker.py",
                CURRENT_DIRECTORY_FULL_PATH + "/test_init_file_checker.py",
            ],
            init_file_checker.find_all_python_files_recursively(CURRENT_DIRECTORY_FULL_PATH),
        )

    def test_find_all_parent_directories(self) -> None:
        """Tests find_all_parent_directories() function."""
        self.assertSetEqual(
            {"/", "/path/", "/path/to/", "/path/to/some/", "/path/to/another/"},
            init_file_checker.find_all_parent_directories(
                ["/path/to/some/file.txt", "/path/to/another/file.txt"],
                "/",
            ),
        )
        self.assertSetEqual(
            {"/path/to/", "/path/to/some/", "/path/to/another/"},
            init_file_checker.find_all_parent_directories(
                ["/path/to/some/file.txt", "/path/to/another/file.txt"],
                "/path/to",
            ),
        )

    def test_find_missing_init_files(self) -> None:
        """Tests find_missing_init_files() function."""
        self.assertListEqual(
            [
                CURRENT_DIRECTORY_FULL_PATH + "/__init__.py",
                CURRENT_DIRECTORY_FULL_PATH + "/.github/__init__.py",
            ],
            init_file_checker.find_missing_init_files([CURRENT_DIRECTORY_FULL_PATH, ".github/"]),
        )


if __name__ == "__main__":
    unittest.main()
