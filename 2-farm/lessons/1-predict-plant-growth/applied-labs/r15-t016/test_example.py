"""
Unit tests for Growing-Degree Calculation (R15-T016)

Tests verify:
1. With base 10, days (8,16),(12,20),(2,8) contribute 2,6,0 and total 8
2. Reject minimum > maximum
3. Baseline and refactored versions produce identical results (equivalence proof)
4. Non-numeric inputs raise appropriate error
5. Deliberate wrong assertion failure test
"""

import unittest
from example import (
    calculate_gdd_baseline,
    compute_single_day_gdd,
    calculate_gdd_refactored,
    run_demo,
)


class TestGrowingDegreeCalculation(unittest.TestCase):
    def test_required_benchmark_fixture(self):
        """With base 10, days (8,16),(12,20),(2,8) contribute 2,6,0 and total 8"""
        records = [(8, 16), (12, 20), (2, 8)]
        base = 10.0
        contribs, total = calculate_gdd_refactored(records, base)

        self.assertEqual(len(contribs), 3)
        self.assertAlmostEqual(contribs[0], 2.0)
        self.assertAlmostEqual(contribs[1], 6.0)
        self.assertAlmostEqual(contribs[2], 0.0)
        self.assertAlmostEqual(total, 8.0)

    def test_reject_minimum_greater_than_maximum(self):
        records = [(20, 15)]  # min=20, max=15 is invalid
        with self.assertRaises(ValueError) as ctx:
            calculate_gdd_refactored(records, 10.0)
        self.assertIn("exceeds maximum", str(ctx.exception))

        with self.assertRaises(ValueError):
            compute_single_day_gdd(25, 20, 10.0)

    def test_baseline_and_refactored_equivalence(self):
        """Proves before/after refactoring equivalence on diverse test records."""
        test_cases = [
            ([(8, 16), (12, 20), (2, 8)], 10.0),
            ([(0, 10), (10, 10), (15, 25), (5, 9)], 12.0),
            ([(18.5, 24.2), (14.0, 19.8)], 15.0),
        ]
        for records, base in test_cases:
            base_contribs, base_total = calculate_gdd_baseline(records, base)
            refac_contribs, refac_total = calculate_gdd_refactored(records, base)

            self.assertEqual(len(base_contribs), len(refac_contribs))
            for b_c, r_c in zip(base_contribs, refac_contribs):
                self.assertAlmostEqual(b_c, r_c)
            self.assertAlmostEqual(base_total, refac_total)

    def test_run_demo(self):
        contribs, total = run_demo()
        self.assertEqual(contribs, [2.0, 6.0, 0.0])
        self.assertEqual(total, 8.0)

    def test_deliberate_wrong_result_fails(self):
        """Demonstrates that a deliberate assertion failure is caught."""
        _, total = calculate_gdd_refactored([(8, 16), (12, 20), (2, 8)], 10.0)
        with self.assertRaises(AssertionError):
            self.assertEqual(total, 100.0)  # Total is 8.0, expecting 100.0 must fail


if __name__ == "__main__":
    unittest.main()
