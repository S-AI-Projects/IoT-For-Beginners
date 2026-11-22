"""
Unit tests for Capability Negotiation (R15-T014)

Tests verify:
1. Client {tools,resources}, server {tools,prompts} negotiates {tools}
2. Calling resources is rejected before dispatch
3. Calling tools succeeds
4. Intermediate state trace records every step
5. State-to-output invariant is preserved
6. Deliberate wrong assertion failure test
"""

import unittest
from example import NegotiationSession, run_demo


class TestCapabilityNegotiation(unittest.TestCase):
    def setUp(self):
        self.client_caps = {"tools", "resources"}
        self.server_caps = {"tools", "prompts"}
        self.session = NegotiationSession(self.client_caps, self.server_caps)

    def test_negotiation_set_intersection(self):
        negotiated = self.session.negotiate()
        self.assertEqual(negotiated, {"tools"})
        self.assertIn("tools", self.session.negotiated_capabilities)
        self.assertNotIn("resources", self.session.negotiated_capabilities)
        self.assertNotIn("prompts", self.session.negotiated_capabilities)

    def test_calling_resources_rejected_before_dispatch(self):
        self.session.negotiate()
        allowed, msg = self.session.dispatch("resources")
        self.assertFalse(allowed)
        self.assertIn("REJECTED: Capability 'resources' was not negotiated", msg)

        # Invariant verification
        self.assertTrue(self.session.verify_invariant("resources", allowed))

    def test_calling_negotiated_capability_succeeds(self):
        self.session.negotiate()
        allowed, msg = self.session.dispatch("tools", {"action": "detect"})
        self.assertTrue(allowed)
        self.assertIn("SUCCESS", msg)

        # Invariant verification
        self.assertTrue(self.session.verify_invariant("tools", allowed))

    def test_calling_before_negotiation_rejected(self):
        # Dispatch before calling negotiate()
        allowed, msg = self.session.dispatch("tools")
        self.assertFalse(allowed)
        self.assertIn("Negotiation has not taken place", msg)

    def test_intermediate_state_trace_completeness(self):
        self.session.negotiate()
        self.session.dispatch("resources")
        self.session.dispatch("tools", {"test": 1})

        steps = [entry["step"] for entry in self.session.state_trace]
        self.assertEqual(steps, ["INIT", "NEGOTIATE", "DISPATCH_REJECTED", "DISPATCH_SUCCESS"])

    def test_run_demo_executes_correctly(self):
        session = run_demo()
        self.assertEqual(session.negotiated_capabilities, {"tools"})

    def test_deliberate_wrong_result_fails(self):
        """Demonstrates that a deliberate assertion failure is caught."""
        self.session.negotiate()
        allowed, _ = self.session.dispatch("resources")
        with self.assertRaises(AssertionError):
            self.assertTrue(allowed)  # Deliberate failure: resources must be False


if __name__ == "__main__":
    unittest.main()
