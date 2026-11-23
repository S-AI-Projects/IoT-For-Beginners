"""Standard-library tests for the fictional, structure-only rubric."""

import copy
import os
import unittest

from example import SCENARIOS, check_scenario


class ScenarioRubricTests(unittest.TestCase):
    def test_exactly_three_fictional_scenarios_pass(self):
        self.assertEqual(len(SCENARIOS), 3)
        for name, scenario in SCENARIOS.items():
            with self.subTest(name=name):
                self.assertEqual(set(scenario), {"asset", "threat", "control", "residual_risk"})
                self.assertEqual(check_scenario(scenario)["status"], "PASS")

    def test_missing_asset_fails(self):
        scenario = copy.deepcopy(SCENARIOS["Spoofed timer completion"])
        del scenario["asset"]
        result = check_scenario(scenario)
        self.assertEqual(result["status"], "FAIL")
        self.assertIn("asset", result["reason"])

    def test_empty_asset_fails(self):
        scenario = copy.deepcopy(SCENARIOS["Spoofed timer completion"])
        scenario["asset"] = "   "
        self.assertEqual(check_scenario(scenario)["status"], "FAIL")

    def test_mismatched_threat_control_is_review_not_fail(self):
        scenario = copy.deepcopy(SCENARIOS["Spoofed timer completion"])
        scenario["control"] = "[privacy] Mute labels so bystanders cannot hear them."
        result = check_scenario(scenario)
        self.assertEqual(result["status"], "REVIEW")
        self.assertIn("human review", result["reason"])

    def test_untagged_control_is_review_not_fail(self):
        scenario = copy.deepcopy(SCENARIOS["Changed timer duration"])
        scenario["control"] = "Ask the user to confirm the time."
        self.assertEqual(check_scenario(scenario)["status"], "REVIEW")

    def test_a_wrong_expectation_is_detectable(self):
        # unittest must reject the deliberately wrong expectation, even
        # though the standard test suite itself should still pass.
        actual = check_scenario(SCENARIOS["Spoofed timer completion"])["status"]
        with self.assertRaises(AssertionError):
            self.assertEqual(actual, "FAIL")  # Incorrect on purpose: actual is PASS.

    @unittest.skipUnless(os.environ.get("R15_T041_NEGATIVE_TEST") == "1",
                         "opt-in deliberate failure; run with R15_T041_NEGATIVE_TEST=1")
    def test_opt_in_deliberately_wrong_expectation(self):
        # Run with R15_T041_NEGATIVE_TEST=1: this MUST fail and exit nonzero.
        actual = check_scenario(SCENARIOS["Spoofed timer completion"])["status"]
        self.assertEqual(actual, "FAIL")  # Deliberately incorrect expectation.


if __name__ == "__main__":
    unittest.main()
