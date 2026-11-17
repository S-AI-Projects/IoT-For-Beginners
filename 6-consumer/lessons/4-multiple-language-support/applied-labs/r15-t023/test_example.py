"""Unit tests for Security Scenario Rubric Checker (Task R15-T023).

Verifies the transparent security scenario rubric, handling of complete scenarios (PASS),
missing assets (FAIL), unrelated controls (REVIEW), and explicit expected-table comparison.
"""

import os
import sys
import unittest

# Ensure the module directory is accessible for direct execution or discovery
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from example import (  # noqa: E402
    compare_approaches,
    demonstrate_mismatch_detection,
    evaluate_scenario,
    get_expected_results_table,
    get_fixture_scenarios,
    is_control_related,
)


class TestSecurityScenarioRubric(unittest.TestCase):
    """Test suite for security scenario rubric evaluation and comparison."""

    def setUp(self) -> None:
        """Set up fixture mapping for targeted scenario tests."""
        self.scenarios_by_id = {s["id"]: s for s in get_fixture_scenarios()}
        self.expected_table = get_expected_results_table()

    # 1. Complete scenarios returning PASS
    def test_pass_credentials_scenario(self) -> None:
        """Test that the translation API credentials scenario returns PASS."""
        sc = self.scenarios_by_id["scenario_credentials"]
        verdict, reason = evaluate_scenario(sc)
        self.assertEqual(verdict, "PASS")
        self.assertIn("complete", reason.lower())

    def test_pass_user_input_scenario(self) -> None:
        """Test that the user-provided translation input scenario returns PASS."""
        sc = self.scenarios_by_id["scenario_user_input"]
        verdict, reason = evaluate_scenario(sc)
        self.assertEqual(verdict, "PASS")
        self.assertIn("complete", reason.lower())

    def test_pass_translated_response_scenario(self) -> None:
        """Test that the translated response scenario returns PASS."""
        sc = self.scenarios_by_id["scenario_translated_response"]
        verdict, reason = evaluate_scenario(sc)
        self.assertEqual(verdict, "PASS")
        self.assertIn("complete", reason.lower())

    # 2. Missing-asset returning FAIL
    def test_fail_missing_asset_field(self) -> None:
        """Test that an omitted asset field returns FAIL."""
        sc = self.scenarios_by_id["scenario_missing_asset"]
        verdict, reason = evaluate_scenario(sc)
        self.assertEqual(verdict, "FAIL")
        self.assertIn("asset", reason.lower())

    def test_fail_empty_asset_string(self) -> None:
        """Test that an asset containing only whitespace returns FAIL."""
        empty_asset_sc = {
            "id": "scenario_empty_asset",
            "asset": "   ",
            "threat": "API key theft",
            "control": "Store keys in Key Vault",
            "residual_risk": "Vault breach",
        }
        verdict, reason = evaluate_scenario(empty_asset_sc)
        self.assertEqual(verdict, "FAIL")
        self.assertIn("asset", reason.lower())

    # 3. Unrelated-control returning REVIEW
    def test_review_unrelated_control(self) -> None:
        """Test that a control unrelated to its named threat returns REVIEW."""
        sc = self.scenarios_by_id["scenario_unrelated_control"]
        verdict, reason = evaluate_scenario(sc)
        self.assertEqual(verdict, "REVIEW")
        self.assertIn("unrelated", reason.lower())

    def test_is_control_related_helper(self) -> None:
        """Test the is_control_related helper function directly."""
        related = is_control_related(
            "Hardcoded credentials in code leading to API key theft",
            "Store keys securely in Azure Key Vault and environment variables",
        )
        self.assertTrue(related)

        unrelated = is_control_related(
            "Hardcoded credentials in code leading to API key theft",
            "Paint the IoT device case bright red with fluorescent stripes",
        )
        self.assertFalse(unrelated)

    # 4. Expected-table comparison and mismatch detection
    def test_approach_comparison_match(self) -> None:
        """Test that Approach A results match Approach B expected table."""
        actual_results = {s["id"]: evaluate_scenario(s)[0] for s in get_fixture_scenarios()}
        self.assertTrue(compare_approaches(actual_results, self.expected_table))

    def test_approach_comparison_detects_mismatch(self) -> None:
        """Test that an incorrect expected result raises an AssertionError."""
        actual_results = {"scenario_credentials": "PASS", "scenario_missing_asset": "FAIL"}
        wrong_expected = {"scenario_credentials": "PASS", "scenario_missing_asset": "PASS"}

        with self.assertRaises(AssertionError) as ctx:
            compare_approaches(actual_results, wrong_expected)
        self.assertIn("scenario_missing_asset", str(ctx.exception))

    def test_approach_comparison_detects_extra_scenario(self) -> None:
        """Test that an unexpected extra scenario ID raises an AssertionError."""
        actual_results = {
            "scenario_credentials": "PASS",
            "scenario_extra_unexpected": "PASS",
        }
        expected_table = {"scenario_credentials": "PASS"}

        with self.assertRaises(AssertionError) as ctx:
            compare_approaches(actual_results, expected_table)
        self.assertIn("Unexpected extra scenario ID", str(ctx.exception))
        self.assertIn("scenario_extra_unexpected", str(ctx.exception))

    def test_approach_comparison_detects_missing_scenario(self) -> None:
        """Test that a scenario ID expected but missing from actual results raises an AssertionError."""
        actual_results = {"scenario_credentials": "PASS"}
        expected_table = {
            "scenario_credentials": "PASS",
            "scenario_missing_from_actual": "PASS",
        }

        with self.assertRaises(AssertionError) as ctx:
            compare_approaches(actual_results, expected_table)
        self.assertIn("Missing scenario ID", str(ctx.exception))
        self.assertIn("scenario_missing_from_actual", str(ctx.exception))

    def test_demonstrate_mismatch_detection_function(self) -> None:
        """Test that demonstrate_mismatch_detection successfully executes and catches errors."""
        self.assertTrue(demonstrate_mismatch_detection())

    # 5. Missing other required fields
    def test_fail_missing_other_required_fields(self) -> None:
        """Test that missing threat, control, or residual_risk fields also return FAIL."""
        missing_threat = {
            "asset": "API Key",
            "control": "Use Key Vault",
            "residual_risk": "Vault breach",
        }
        verdict, reason = evaluate_scenario(missing_threat)
        self.assertEqual(verdict, "FAIL")
        self.assertIn("threat", reason.lower())


if __name__ == "__main__":
    unittest.main()
