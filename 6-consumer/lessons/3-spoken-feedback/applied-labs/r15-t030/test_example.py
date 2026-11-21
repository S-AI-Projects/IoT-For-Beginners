#!/usr/bin/env python3
"""Unit tests for Security-Scenario Rubric assessment.

Coursework Task: R15-T030
Context Lesson: 6-consumer/lessons/3-spoken-feedback
"""

import os
import subprocess
import sys
import unittest

from example import (
    assess_security_scenario,
    get_standard_scenarios,
    verify_scenario_expectations,
)


class TestSecurityScenarioRubric(unittest.TestCase):
    """Test suite covering rubric evaluation, boundary conditions, applied questions, and CLI."""

    def setUp(self):
        self.scenarios = get_standard_scenarios()

    def test_voice_impersonation_scenario_passes(self):
        """Complete voice impersonation scenario with out-of-band confirmation must PASS."""
        sc = self.scenarios["SCENARIO_1_VOICE"]
        verdict = assess_security_scenario(sc)
        self.assertEqual(verdict.status, "PASS")
        self.assertEqual(verdict.matched_threat_domain, "voice_impersonation")
        self.assertIn("matched predefined control keywords", verdict.reason)
        self.assertIn("predefined keyword heuristic", verdict.reason)
        self.assertIn("does not prove control effectiveness", verdict.reason)

    def test_timer_request_scenario_passes(self):
        """Complete timer request manipulation scenario with validation must PASS."""
        sc = self.scenarios["SCENARIO_2_TIMER"]
        verdict = assess_security_scenario(sc)
        self.assertEqual(verdict.status, "PASS")
        self.assertEqual(verdict.matched_threat_domain, "timer_request")

    def test_ssml_manipulation_scenario_passes(self):
        """Complete SSML manipulation scenario with escaping and allow-listing must PASS."""
        sc = self.scenarios["SCENARIO_3_SSML"]
        verdict = assess_security_scenario(sc)
        self.assertEqual(verdict.status, "PASS")
        self.assertEqual(verdict.matched_threat_domain, "ssml_manipulation")

    def test_missing_asset_scenario_fails(self):
        """Scenario missing the required 'asset' field must return FAIL."""
        sc = self.scenarios["SCENARIO_4_MISSING_ASSET"]
        verdict = assess_security_scenario(sc)
        self.assertEqual(verdict.status, "FAIL")
        self.assertEqual(verdict.missing_field, "asset")
        self.assertIn("Missing required field: 'asset'", verdict.reason)

    def test_blank_field_fails(self):
        """Scenario with whitespace-only required field must return FAIL."""
        blank_sc = {
            "asset": "Spoken feedback integrity",
            "threat": "   ",  # Blank threat
            "control": "Enforce escaping",
            "residual_risk": "None",
        }
        verdict = assess_security_scenario(blank_sc)
        self.assertEqual(verdict.status, "FAIL")
        self.assertEqual(verdict.missing_field, "threat")
        self.assertIn("cannot be empty or whitespace", verdict.reason)

    def test_missing_control_fails(self):
        """Scenario missing 'control' must return FAIL."""
        sc = {
            "asset": "Spoken feedback",
            "threat": "SSML injection",
            "residual_risk": "None",
        }
        verdict = assess_security_scenario(sc)
        self.assertEqual(verdict.status, "FAIL")
        self.assertEqual(verdict.missing_field, "control")

    def test_missing_residual_risk_fails(self):
        """Scenario missing 'residual_risk' must return FAIL."""
        sc = {
            "asset": "Spoken feedback",
            "threat": "SSML injection",
            "control": "Sanitize and escape input",
        }
        verdict = assess_security_scenario(sc)
        self.assertEqual(verdict.status, "FAIL")
        self.assertEqual(verdict.missing_field, "residual_risk")

    def test_unrelated_control_triggers_review(self):
        """Complete scenario with unrelated control (e.g. painting casing) must return REVIEW."""
        sc = self.scenarios["SCENARIO_5_UNRELATED_CONTROL"]
        verdict = assess_security_scenario(sc)
        self.assertEqual(verdict.status, "REVIEW")
        self.assertEqual(verdict.matched_threat_domain, "ssml_manipulation")
        self.assertIn("lacks relevant predefined keywords", verdict.reason)

    def test_unrecognized_threat_triggers_review(self):
        """Complete scenario with an unknown threat domain must return REVIEW."""
        sc = {
            "asset": "Factory floor lighting",
            "threat": "Power fluctuation in secondary grid",
            "control": "Install uninterruptible power supply (UPS)",
            "residual_risk": "Battery degradation over time",
        }
        verdict = assess_security_scenario(sc)
        self.assertEqual(verdict.status, "REVIEW")
        self.assertIn("Threat domain unrecognized", verdict.reason)

    # --- Tests for the Three Applied Questions ---

    def test_applied_question_1_predict_output(self):
        """Q1: What status does the complete voice-impersonation scenario receive? Expected: PASS."""
        sc = self.scenarios["SCENARIO_1_VOICE"]
        # Verify all four required fields are populated
        for field in ("asset", "threat", "control", "residual_risk"):
            self.assertIn(field, sc)
            self.assertIsInstance(sc[field], str)
            self.assertTrue(len(sc[field].strip()) > 0)
        verdict = assess_security_scenario(sc)
        self.assertEqual(verdict.status, "PASS")
        self.assertIn("matched predefined control keywords", verdict.reason)
        self.assertIn("predefined keyword heuristic", verdict.reason)

    def test_applied_question_2_diagnose_failure(self):
        """Q2: Why does a timer scenario with no asset fail? Expected: FAIL with missing-field explanation."""
        sc = self.scenarios["SCENARIO_4_MISSING_ASSET"]
        self.assertNotIn("asset", sc)
        verdict = assess_security_scenario(sc)
        self.assertEqual(verdict.status, "FAIL")
        self.assertEqual(verdict.missing_field, "asset")
        self.assertIn("Missing required field: 'asset'", verdict.reason)

    def test_applied_question_3_choose_boundary_policy(self):
        """Q3: What should happen when an SSML scenario proposes an unrelated control? Expected: REVIEW."""
        sc = self.scenarios["SCENARIO_5_UNRELATED_CONTROL"]
        verdict = assess_security_scenario(sc)
        self.assertEqual(verdict.status, "REVIEW")
        self.assertNotEqual(verdict.status, "PASS")
        self.assertIn("lacks relevant predefined keywords", verdict.reason)

    # --- Verification Function & Mismatch Tests ---

    def test_verify_scenario_expectations_success(self):
        """verify_scenario_expectations succeeds when all outcomes match expected table."""
        eval_list = [
            self.scenarios["SCENARIO_1_VOICE"],
            self.scenarios["SCENARIO_2_TIMER"],
            self.scenarios["SCENARIO_3_SSML"],
            self.scenarios["SCENARIO_4_MISSING_ASSET"],
            self.scenarios["SCENARIO_5_UNRELATED_CONTROL"],
        ]
        expected_table = {
            "SCENARIO_1_VOICE": "PASS",
            "SCENARIO_2_TIMER": "PASS",
            "SCENARIO_3_SSML": "PASS",
            "SCENARIO_4_MISSING_ASSET": "FAIL",
            "SCENARIO_5_UNRELATED_CONTROL": "REVIEW",
        }
        results = verify_scenario_expectations(eval_list, expected_table)
        self.assertEqual(len(results), 5)
        for sc_id, exp, act in results:
            self.assertEqual(exp, act)

    def test_verify_scenario_missing_from_expected_table(self):
        """verify_scenario_expectations raises AssertionError when a scenario is missing from expected_table."""
        eval_list = [
            self.scenarios["SCENARIO_1_VOICE"],
            self.scenarios["SCENARIO_2_TIMER"],
        ]
        incomplete_table = {
            "SCENARIO_1_VOICE": "PASS",
            # SCENARIO_2_TIMER is intentionally missing
        }
        with self.assertRaises(AssertionError) as ctx:
            verify_scenario_expectations(eval_list, incomplete_table)

        self.assertIn("Scenario 'SCENARIO_2_TIMER' is missing from the expected-results table", str(ctx.exception))

    def test_verify_unexpected_extra_id_in_expected_table(self):
        """verify_scenario_expectations raises AssertionError when expected_table has IDs not supplied."""
        eval_list = [
            self.scenarios["SCENARIO_1_VOICE"],
        ]
        extra_table = {
            "SCENARIO_1_VOICE": "PASS",
            "SCENARIO_NONEXISTENT": "PASS",
        }
        with self.assertRaises(AssertionError) as ctx:
            verify_scenario_expectations(eval_list, extra_table)

        self.assertIn("SCENARIO_NONEXISTENT", str(ctx.exception))
        self.assertIn("unexpected scenario ID(s) for which no scenario was supplied", str(ctx.exception))

    def test_deliberate_wrong_expected_result_detected(self):
        """verify_scenario_expectations raises AssertionError when an outcome differs from expected."""
        eval_list = [self.scenarios["SCENARIO_1_VOICE"]]  # Actually PASS
        corrupted_table = {"SCENARIO_1_VOICE": "FAIL"}    # Wrong expected

        with self.assertRaises(AssertionError) as ctx:
            verify_scenario_expectations(eval_list, corrupted_table)

        self.assertIn("Outcome mismatch for scenario 'SCENARIO_1_VOICE'", str(ctx.exception))
        self.assertIn("expected 'FAIL', got 'PASS'", str(ctx.exception))

    # --- Subprocess CLI Tests ---

    def test_cli_normal_scenario_subprocess(self):
        """CLI --scenario normal runs in fresh process, exits 0, and reports all normal scenarios pass."""
        lab_dir = os.path.dirname(os.path.abspath(__file__))
        example_path = os.path.join(lab_dir, "example.py")

        cmd = [sys.executable, example_path, "--scenario", "normal"]
        proc = subprocess.run(cmd, capture_output=True, text=True)

        self.assertEqual(proc.returncode, 0, f"Error:\n{proc.stderr}")
        self.assertIn("SCENARIO_1_VOICE", proc.stdout)
        self.assertIn("SCENARIO_2_TIMER", proc.stdout)
        self.assertIn("SCENARIO_3_SSML", proc.stdout)
        self.assertIn("All normal scenarios successfully passed", proc.stdout)

    def test_cli_boundary_scenario_subprocess(self):
        """CLI --scenario boundary runs in fresh process, exits 0, and reports boundary checks pass."""
        lab_dir = os.path.dirname(os.path.abspath(__file__))
        example_path = os.path.join(lab_dir, "example.py")

        cmd = [sys.executable, example_path, "--scenario", "boundary"]
        proc = subprocess.run(cmd, capture_output=True, text=True)

        self.assertEqual(proc.returncode, 0, f"Error:\n{proc.stderr}")
        self.assertIn("SCENARIO_4_MISSING_ASSET", proc.stdout)
        self.assertIn("SCENARIO_5_UNRELATED_CONTROL", proc.stdout)
        self.assertIn("All boundary conditions handled cleanly", proc.stdout)

    def test_cli_failure_scenario_subprocess(self):
        """CLI --scenario failure runs in fresh process and exits non-zero with intentional failure message."""
        lab_dir = os.path.dirname(os.path.abspath(__file__))
        example_path = os.path.join(lab_dir, "example.py")

        cmd = [sys.executable, example_path, "--scenario", "failure"]
        proc = subprocess.run(cmd, capture_output=True, text=True)

        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("INTENTIONAL FAILURE", proc.stdout + proc.stderr)
        self.assertIn("Outcome mismatch for scenario", proc.stderr + proc.stdout)


if __name__ == "__main__":
    unittest.main()
