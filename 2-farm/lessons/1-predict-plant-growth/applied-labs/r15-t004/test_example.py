import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from example import (  # noqa: E402
    calculate_daily_gdd,
    calculate_gdd_with_trace,
)


class TestGrowingDegreeCalculation(unittest.TestCase):
    def test_sample_days_and_accumulation(self):
        """With base 10, days (8,16),(12,20),(2,8) contribute 2,6,0 and total 8."""
        records = [(8, 16), (12, 20), (2, 8)]
        res = calculate_gdd_with_trace(records, base_temp=10)

        self.assertEqual(res["contributions"], [2.0, 6.0, 0.0])
        self.assertEqual(res["total_gdd"], 8.0)

    def test_state_trace_and_invariants(self):
        """Verify the state trace invariant: accumulated_gdd == sum(daily_gdd) at each step."""
        records = [(8, 16), (12, 20), (2, 8), (15, 25), (5, 9)]
        res = calculate_gdd_with_trace(records, base_temp=10)
        trace = res["trace"]

        self.assertEqual(len(trace), 5)
        running_sum = 0.0
        for step in trace:
            # Invariant 1: daily contribution is non-negative
            self.assertGreaterEqual(step["daily_gdd"], 0.0)
            running_sum += step["daily_gdd"]
            # Invariant 2: step accumulated value matches exact prefix sum
            self.assertEqual(step["accumulated_gdd"], running_sum)

        # Invariant 3: final accumulated matches total_gdd
        self.assertEqual(trace[-1]["accumulated_gdd"], res["total_gdd"])

    def test_rejection_of_minimum_greater_than_maximum(self):
        """Reject records where minimum > maximum."""
        with self.assertRaises(ValueError):
            calculate_daily_gdd(min_temp=25, max_temp=20, base_temp=10)

        with self.assertRaises(ValueError):
            calculate_gdd_with_trace([(10, 15), (22, 18)], base_temp=10)

    def test_invalid_types_rejected(self):
        """Non-numeric values raise TypeError."""
        with self.assertRaises(TypeError):
            calculate_daily_gdd("10", 20, 10)
        with self.assertRaises(TypeError):
            calculate_daily_gdd(10, None, 10)
        with self.assertRaises(TypeError):
            calculate_daily_gdd(10, 20, "10")

    def test_equal_min_and_max(self):
        """Boundary condition: min == max is accepted."""
        daily, mean = calculate_daily_gdd(15, 15, 10)
        self.assertEqual(mean, 15.0)
        self.assertEqual(daily, 5.0)


if __name__ == "__main__":
    unittest.main()
