import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from example import (SCENARIOS, check_scenario, check_scenario_baseline,  # noqa: E402
                     control_addresses_threat, missing_fields)


class Rubric(unittest.TestCase):
    def test_complete_scenario_passes(self):
        self.assertEqual(check_scenario(SCENARIOS[0]), {"status": "pass", "problems": []})

    def test_missing_asset_fails(self):
        r = check_scenario(SCENARIOS[1])
        self.assertEqual(r["status"], "fail")
        self.assertIn("missing asset", r["problems"])

    def test_unrelated_control_flagged_for_review(self):
        r = check_scenario(SCENARIOS[2])
        self.assertEqual(r["status"], "review")

    def test_each_field_is_required(self):
        for f in ("asset", "threat", "control", "residual_risk"):
            s = dict(SCENARIOS[0])
            del s[f]
            with self.subTest(field=f):
                self.assertEqual(check_scenario(s)["status"], "fail")

    def test_blank_and_non_string_fields_fail(self):
        for bad in ["   ", None, 5]:
            s = dict(SCENARIOS[0], asset=bad)
            self.assertEqual(check_scenario(s)["status"], "fail")

    def test_not_a_dict_fails(self):
        self.assertEqual(check_scenario(None)["status"], "fail")

    def test_unknown_threat_goes_to_review(self):
        s = dict(SCENARIOS[0], threat="meteor strike")
        self.assertEqual(check_scenario(s)["status"], "review")


class RefactorEquivalence(unittest.TestCase):
    """Baseline and refactored versions must give identical results."""

    def test_equivalent_on_fixture(self):
        for s in SCENARIOS:
            with self.subTest(name=s["name"]):
                self.assertEqual(check_scenario_baseline(s), check_scenario(s))

    def test_equivalent_on_variations(self):
        variants = []
        for s in SCENARIOS:
            for f in ("asset", "threat", "control", "residual_risk"):
                variants.append(dict(s, **{f: ""}))
                v = dict(s)
                v.pop(f)
                variants.append(v)
        variants += [None, {}, "text", dict(SCENARIOS[0], threat="meteor")]
        for v in variants:
            self.assertEqual(check_scenario_baseline(v), check_scenario(v))

    def test_extracted_responsibility(self):
        self.assertTrue(control_addresses_threat("Key exposure", "Use a KEY VAULT"))
        self.assertFalse(control_addresses_threat("key exposure", "use https"))
        self.assertEqual(missing_fields({"asset": "a"}),
                         ["missing threat", "missing control", "missing residual_risk"])


if __name__ == "__main__":
    unittest.main()
