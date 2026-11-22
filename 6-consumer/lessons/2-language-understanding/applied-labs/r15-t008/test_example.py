import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from example import AccessPolicyEvaluator  # noqa: E402


class TestAccessPolicyEvaluation(unittest.TestCase):
    def setUp(self):
        self.evaluator = AccessPolicyEvaluator()

    def test_reader_may_read_public(self):
        """reader may read public."""
        decision, reason = self.evaluator.evaluate("reader", "read", "public")
        self.assertEqual(decision, "allow")
        self.assertIn("allow", reason.lower())

    def test_reader_cannot_write(self):
        """reader cannot write."""
        decision, reason = self.evaluator.evaluate("reader", "write", "public")
        self.assertEqual(decision, "deny")
        self.assertIn("default deny", reason.lower())

    def test_explicit_deny_overrides_matching_allow(self):
        """an explicit deny overrides a matching allow."""
        # editor can write normal resource
        self.assertEqual(self.evaluator.evaluate("editor", "write", "notes")[0], "allow")
        # editor writing locked resource is explicitly denied
        decision, reason = self.evaluator.evaluate("editor", "write", "locked")
        self.assertEqual(decision, "deny")
        self.assertIn("explicit deny", reason.lower())

    def test_unknown_role_is_denied(self):
        """an unknown role is denied."""
        decision, reason = self.evaluator.evaluate("guest", "read", "public")
        self.assertEqual(decision, "deny")
        self.assertIn("unknown role", reason.lower())

    def test_failure_and_recovery_sequence(self):
        """Exercise documented invalid/missing-data case and demonstrate recovery on next input."""
        # Baseline valid request
        self.assertEqual(self.evaluator.evaluate("reader", "read", "public")[0], "allow")

        # 1. Exercise documented missing/invalid input: empty action
        decision, reason = self.evaluator.evaluate("reader", "", "public")
        self.assertEqual(decision, "deny")
        self.assertIn("cannot be empty", reason)
        self.assertEqual(self.evaluator.error_count, 1)

        # 2. Exercise None / bad type input
        decision2, reason2 = self.evaluator.evaluate("reader", None, "public")
        self.assertEqual(decision2, "deny")
        self.assertIn("non-null strings", reason2)
        self.assertEqual(self.evaluator.error_count, 2)

        # 3. Demonstrate recovery on immediate next valid input
        decision3, reason3 = self.evaluator.evaluate("reader", "read", "public")
        self.assertEqual(decision3, "allow")
        self.assertIn("allow", reason3.lower())


if __name__ == "__main__":
    unittest.main()
