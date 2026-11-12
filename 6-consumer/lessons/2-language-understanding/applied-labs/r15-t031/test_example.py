import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from example import evaluate  # noqa: E402


class SmallestValid(unittest.TestCase):
    def test_reader_reads_public(self):
        self.assertEqual(evaluate("reader", "read", "public")[0], "allow")


class Boundary(unittest.TestCase):
    def test_reader_cannot_write_public(self):
        self.assertEqual(evaluate("reader", "write", "public"),
                         ("deny", "default deny"))

    def test_reader_cannot_read_private(self):
        self.assertEqual(evaluate("reader", "read", "private")[0], "deny")

    def test_deny_overrides_allow(self):
        self.assertEqual(evaluate("editor", "write", "locked"),
                         ("deny", "explicit deny"))
        self.assertEqual(evaluate("editor", "write", "notes")[0], "allow")

    def test_admin_wildcard(self):
        self.assertEqual(evaluate("admin", "delete", "anything")[0], "allow")


class Invalid(unittest.TestCase):
    def test_unknown_role(self):
        self.assertEqual(evaluate("guest", "read", "public"),
                         ("deny", "unknown role"))

    def test_empty_and_wrong_types(self):
        for bad in [("", "read", "public"), ("reader", None, "public"),
                    ("reader", "read", 5)]:
            self.assertEqual(evaluate(*bad)[0], "deny")


if __name__ == "__main__":
    unittest.main()
