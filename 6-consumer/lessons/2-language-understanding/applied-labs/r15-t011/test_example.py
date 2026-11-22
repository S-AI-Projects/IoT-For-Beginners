"""
Unit tests for Explicit Access-Policy Evaluation (R15-T011)

Tests verify:
1. reader may read public
2. reader cannot write
3. explicit deny overrides matching allow
4. unknown role is denied
5. deliberate wrong result fails test assertions
"""

import unittest
from example import (
    DEFAULT_POLICY_MATRIX,
    PolicyRule,
    evaluate_access,
    run_demo,
)


class TestAccessPolicyEvaluation(unittest.TestCase):
    def test_reader_may_read_public(self):
        allowed, reason = evaluate_access("reader", "read", "public")
        self.assertTrue(allowed, f"Expected reader to read public, got {reason}")
        self.assertIn("ALLOW", reason)

    def test_reader_cannot_write(self):
        allowed, reason = evaluate_access("reader", "write", "public")
        self.assertFalse(allowed, f"Expected reader write to be denied, got {reason}")
        self.assertIn("DENY", reason)

    def test_explicit_deny_overrides_matching_allow(self):
        # editor has ALLOW read * and ALLOW write public, but explicit DENY write restricted
        allowed, reason = evaluate_access("editor", "write", "restricted")
        self.assertFalse(allowed, f"Expected explicit deny to override allow, got {reason}")
        self.assertIn("Explicit deny rule matched", reason)

        # admin has ALLOW * *, but DENY delete system-root
        admin_allowed, admin_reason = evaluate_access("admin", "delete", "system-root")
        self.assertFalse(admin_allowed)
        self.assertIn("Explicit deny rule matched", admin_reason)

    def test_unknown_role_is_denied(self):
        allowed, reason = evaluate_access("intruder", "read", "public")
        self.assertFalse(allowed, f"Expected unknown role to be denied, got {reason}")
        self.assertIn("Role 'intruder' is unknown", reason)

    def test_default_deny_when_no_rule_matches(self):
        # reader requesting an unmapped resource
        allowed, reason = evaluate_access("reader", "manage", "unknown-resource")
        self.assertFalse(allowed)
        self.assertIn("Default deny", reason)

    def test_run_demo_executes_successfully(self):
        results = run_demo()
        self.assertEqual(len(results), 4)
        self.assertTrue(results["reader_read_public"][0])
        self.assertFalse(results["reader_write_public"][0])
        self.assertFalse(results["editor_write_restricted"][0])
        self.assertFalse(results["unknown_role_read"][0])

    def test_deliberate_wrong_result_fails(self):
        """Demonstrates that a deliberate assertion failure is caught."""
        allowed, _ = evaluate_access("reader", "read", "public")
        # An incorrect expectation that reader reading public is False should fail
        with self.assertRaises(AssertionError):
            self.assertFalse(allowed)


if __name__ == "__main__":
    unittest.main()
