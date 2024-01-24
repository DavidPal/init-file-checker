"""Unit tests for init_file_checker module."""

import re
import unittest

import init_file_checker


def extract_version_from_pyproject():
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

    def test_check_version(self):
        """Verify that version numbers are the same in all places."""
        self.assertEqual(init_file_checker.VERSION, extract_version_from_pyproject())

    def test_dummy(self):
        """Tests equality of Lines."""
        self.assertEqual(2, 1 + 1)


if __name__ == "__main__":
    unittest.main()
