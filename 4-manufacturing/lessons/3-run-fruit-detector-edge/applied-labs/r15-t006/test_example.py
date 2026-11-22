import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from example import (  # noqa: E402
    check_rubric,
    evaluate_scenario_baseline,
    SCENARIO_1_COMPLETE,
    SCENARIO_2_COMPLETE,
    SCENARIO_3_COMPLETE,
    SCENARIO_MISSING_ASSET,
    SCENARIO_UNRELATED_CONTROL,
)


class TestSecurityScenarioRubric(unittest.TestCase):
    def test_complete_scenarios_pass(self):
        """One complete scenario passes."""
        status1, _ = check_rubric(SCENARIO_1_COMPLETE)
        self.assertEqual(status1, "PASS")

        status2, _ = check_rubric(SCENARIO_2_COMPLETE)
        self.assertEqual(status2, "PASS")

        status3, _ = check_rubric(SCENARIO_3_COMPLETE)
        self.assertEqual(status3, "PASS")

    def test_scenario_without_asset_fails(self):
        """A scenario without an asset fails."""
        status, reason = check_rubric(SCENARIO_MISSING_ASSET)
        self.assertEqual(status, "FAIL")
        self.assertIn("asset", reason)

        # Missing field key completely
        no_asset_dict = {
            "threat": "Tampering",
            "control": "Enclosure",
            "residual_risk": "None",
        }
        self.assertEqual(check_rubric(no_asset_dict)[0], "FAIL")

    def test_unrelated_control_flagged_for_review(self):
        """A control unrelated to the named threat is flagged for review."""
        status, reason = check_rubric(SCENARIO_UNRELATED_CONTROL)
        self.assertEqual(status, "REVIEW")
        self.assertIn("human review", reason.lower())

    def test_refactoring_equivalence(self):
        """Verify before/after equivalence between baseline and refactored implementation."""
        test_cases = [
            SCENARIO_1_COMPLETE,
            SCENARIO_2_COMPLETE,
            SCENARIO_3_COMPLETE,
            SCENARIO_MISSING_ASSET,
            SCENARIO_UNRELATED_CONTROL,
            {},
            {"asset": "Cam", "threat": "tamper", "control": "unrelated", "residual_risk": "R"},
            {"asset": "A", "threat": "intercept", "control": "TLS encryption", "residual_risk": "R"},
        ]

        for sc in test_cases:
            baseline_result = evaluate_scenario_baseline(sc)
            refactored_result = check_rubric(sc)
            self.assertEqual(
                baseline_result,
                refactored_result,
                f"Mismatch on scenario: {sc}",
            )


if __name__ == "__main__":
    unittest.main()
