#!/usr/bin/env python3
"""Unit tests for Growing Degree Days (GDD) calculation and recovery.

Coursework Task: R15-T028
Context: 2-farm/lessons/1-predict-plant-growth
"""

import os
import subprocess
import sys
import unittest

from example import (
    calculate_daily_gdd,
    process_single_record,
    process_temperature_records,
    validate_temperature_value,
)


class TestGrowingDegreeDays(unittest.TestCase):
    """Test suite for GDD calculation, boundary conditions, validations, and recovery."""

    def test_mandatory_daily_values(self):
        """Verify the mandatory daily values: Day 1 -> 2, Day 2 -> 6, Day 3 -> 0."""
        base_temp = 10.0
        # Day 1: min 8, max 16 -> avg 12 -> 12 - 10 = 2
        avg1, gdd1 = calculate_daily_gdd(8, 16, base_temp)
        self.assertEqual(avg1, 12.0)
        self.assertEqual(gdd1, 2.0)

        # Day 2: min 12, max 20 -> avg 16 -> 16 - 10 = 6
        avg2, gdd2 = calculate_daily_gdd(12, 20, base_temp)
        self.assertEqual(avg2, 16.0)
        self.assertEqual(gdd2, 6.0)

        # Day 3: min 2, max 8 -> avg 5 -> max(0, 5 - 10) = 0
        avg3, gdd3 = calculate_daily_gdd(2, 8, base_temp)
        self.assertEqual(avg3, 5.0)
        self.assertEqual(gdd3, 0.0)

    def test_mandatory_accumulated_total(self):
        """Verify that mandatory 3-day fixture produces an accumulated total of exactly 8."""
        records = [
            {"minimum": 8, "maximum": 16},
            {"minimum": 12, "maximum": 20},
            {"minimum": 2, "maximum": 8},
        ]
        results = process_temperature_records(records, base_temp=10.0)
        self.assertEqual(len(results), 3)
        self.assertTrue(all(r.is_valid for r in results))
        self.assertEqual(results[0].accumulated_gdd, 2.0)
        self.assertEqual(results[1].accumulated_gdd, 8.0)
        self.assertEqual(results[2].accumulated_gdd, 8.0)
        self.assertEqual(results[-1].accumulated_gdd, 8.0)

    def test_average_equal_to_base(self):
        """When average temperature equals base temperature, GDD must be exactly 0.0."""
        # Exact equal min and max
        avg, gdd = calculate_daily_gdd(10.0, 10.0, base_temp=10.0)
        self.assertEqual(avg, 10.0)
        self.assertEqual(gdd, 0.0)

        # Equal average (min 8, max 12)
        avg2, gdd2 = calculate_daily_gdd(8.0, 12.0, base_temp=10.0)
        self.assertEqual(avg2, 10.0)
        self.assertEqual(gdd2, 0.0)

    def test_average_below_base(self):
        """When average temperature is below base temperature, GDD must clamp to 0.0."""
        avg, gdd = calculate_daily_gdd(0.0, 10.0, base_temp=10.0)
        self.assertEqual(avg, 5.0)
        self.assertEqual(gdd, 0.0)

        # Negative temperatures
        avg_neg, gdd_neg = calculate_daily_gdd(-10.0, -2.0, base_temp=10.0)
        self.assertEqual(avg_neg, -6.0)
        self.assertEqual(gdd_neg, 0.0)

    def test_missing_minimum(self):
        """A record missing 'minimum' must be rejected with a clear error."""
        res = process_single_record({"maximum": 16}, base_temp=10.0, current_total=5.0, day_index=1)
        self.assertFalse(res.is_valid)
        self.assertEqual(res.daily_gdd, 0.0)
        self.assertEqual(res.accumulated_gdd, 5.0)
        self.assertIn("minimum", res.error_message.lower())

        # Also when minimum is explicitly None
        res_none = process_single_record(
            {"minimum": None, "maximum": 16}, base_temp=10.0, current_total=5.0, day_index=1
        )
        self.assertFalse(res_none.is_valid)
        self.assertIn("minimum", res_none.error_message.lower())

    def test_missing_maximum(self):
        """A record missing 'maximum' must be rejected with a clear error."""
        res = process_single_record({"minimum": 8}, base_temp=10.0, current_total=5.0, day_index=1)
        self.assertFalse(res.is_valid)
        self.assertEqual(res.daily_gdd, 0.0)
        self.assertEqual(res.accumulated_gdd, 5.0)
        self.assertIn("maximum", res.error_message.lower())

        # Also when maximum is explicitly None
        res_none = process_single_record(
            {"minimum": 8, "maximum": None}, base_temp=10.0, current_total=5.0, day_index=1
        )
        self.assertFalse(res_none.is_valid)
        self.assertIn("maximum", res_none.error_message.lower())

    def test_minimum_greater_than_maximum(self):
        """Minimum temperature greater than maximum temperature must be rejected."""
        with self.assertRaises(ValueError) as ctx:
            calculate_daily_gdd(18.0, 14.0, base_temp=10.0)
        self.assertIn("cannot exceed maximum", str(ctx.exception))

        # In record stream
        res = process_single_record(
            {"minimum": 25, "maximum": 15}, base_temp=10.0, current_total=0.0, day_index=1
        )
        self.assertFalse(res.is_valid)
        self.assertIn("cannot exceed maximum", res.error_message)

    def test_boolean_values_rejected(self):
        """Booleans must be explicitly rejected despite being int subclasses in Python."""
        with self.assertRaises(TypeError) as ctx:
            validate_temperature_value(True, "Temperature")
        self.assertIn("boolean", str(ctx.exception))

        with self.assertRaises(TypeError):
            calculate_daily_gdd(False, 16.0, base_temp=10.0)

        with self.assertRaises(TypeError):
            calculate_daily_gdd(8.0, True, base_temp=10.0)

        with self.assertRaises(TypeError):
            calculate_daily_gdd(8.0, 16.0, base_temp=True)

    def test_non_numeric_values_rejected(self):
        """String, list, or None temperature values must be rejected."""
        with self.assertRaises(TypeError):
            validate_temperature_value("25", "Temperature")

        with self.assertRaises(TypeError):
            calculate_daily_gdd("8", 16, base_temp=10.0)

        with self.assertRaises(TypeError):
            calculate_daily_gdd(8, [16], base_temp=10.0)

    def test_nan_and_infinity_rejected(self):
        """NaN and infinite values must raise ValueError."""
        with self.assertRaises(ValueError) as ctx:
            validate_temperature_value(float("nan"), "Temperature")
        self.assertIn("finite number", str(ctx.exception))

        with self.assertRaises(ValueError):
            calculate_daily_gdd(float("inf"), 20.0, base_temp=10.0)

        with self.assertRaises(ValueError):
            calculate_daily_gdd(8.0, float("-inf"), base_temp=10.0)

    def test_overflow_integer_rejected(self):
        """Extremely large integers causing OverflowError on float conversion must raise ValueError."""
        huge_int = 10**10000
        with self.assertRaises(ValueError) as ctx:
            validate_temperature_value(huge_int, "Minimum temperature")
        self.assertIn("supported numeric range", str(ctx.exception))

        with self.assertRaises(ValueError):
            calculate_daily_gdd(huge_int, 20.0, base_temp=10.0)

        res = process_single_record(
            {"minimum": huge_int, "maximum": 20}, base_temp=10.0, current_total=2.0, day_index=2
        )
        self.assertFalse(res.is_valid)
        self.assertIn("supported numeric range", res.error_message)
        self.assertEqual(res.accumulated_gdd, 2.0)

    def test_calculation_overflow_non_finite_rejected(self):
        """Individually finite temperatures whose sum or average overflows must raise ValueError."""
        val = 1e308
        with self.assertRaises(ValueError) as ctx:
            calculate_daily_gdd(val, val, base_temp=10.0)
        self.assertIn("non-finite", str(ctx.exception).lower())

        # Verify that process_single_record marks it invalid and preserves running total
        res = process_single_record(
            {"minimum": val, "maximum": val}, base_temp=10.0, current_total=5.0, day_index=3
        )
        self.assertFalse(res.is_valid)
        self.assertEqual(res.daily_gdd, 0.0)
        self.assertEqual(res.accumulated_gdd, 5.0)
        self.assertIn("non-finite", res.error_message.lower())

        # Verify stream processing with an overflowing record does not corrupt running total
        records = [
            {"minimum": 8, "maximum": 16},     # Day 1: GDD 2, total 2
            {"minimum": val, "maximum": val},   # Day 2: overflow, total remains 2
            {"minimum": 12, "maximum": 20},    # Day 3: GDD 6, total 8 (recovery)
        ]
        results = process_temperature_records(records, base_temp=10.0)
        self.assertEqual(len(results), 3)
        self.assertTrue(results[0].is_valid)
        self.assertEqual(results[0].accumulated_gdd, 2.0)
        self.assertFalse(results[1].is_valid)
        self.assertEqual(results[1].daily_gdd, 0.0)
        self.assertEqual(results[1].accumulated_gdd, 2.0)
        self.assertTrue(results[2].is_valid)
        self.assertEqual(results[2].daily_gdd, 6.0)
        self.assertEqual(results[2].accumulated_gdd, 8.0)

    def test_invalid_records_not_changing_total(self):
        """An invalid record must contribute exactly 0.0 GDD to the accumulated total."""
        records = [
            {"minimum": 8, "maximum": 16},     # valid -> +2 GDD, total 2
            {"minimum": 20, "maximum": 10},    # invalid (min > max) -> +0 GDD, total 2
            {"minimum": "invalid", "maximum": 20}, # invalid (type) -> +0 GDD, total 2
            {"minimum": 12, "maximum": 20},    # valid -> +6 GDD, total 8
        ]
        results = process_temperature_records(records, base_temp=10.0)
        self.assertEqual(len(results), 4)
        self.assertTrue(results[0].is_valid)
        self.assertEqual(results[0].accumulated_gdd, 2.0)

        self.assertFalse(results[1].is_valid)
        self.assertEqual(results[1].daily_gdd, 0.0)
        self.assertEqual(results[1].accumulated_gdd, 2.0)

        self.assertFalse(results[2].is_valid)
        self.assertEqual(results[2].daily_gdd, 0.0)
        self.assertEqual(results[2].accumulated_gdd, 2.0)

        self.assertTrue(results[3].is_valid)
        self.assertEqual(results[3].daily_gdd, 6.0)
        self.assertEqual(results[3].accumulated_gdd, 8.0)

    def test_recovery_after_invalid_record(self):
        """Processing must continue after an invalid record, demonstrating recovery."""
        recovery_stream = [
            {"minimum": 8, "maximum": 16},  # Record 1: Valid, GDD 2
            {"minimum": 8},                 # Record 2: Missing max, invalid
            {"minimum": 12, "maximum": 20}, # Record 3: Valid, GDD 6
        ]
        results = process_temperature_records(recovery_stream, base_temp=10.0)
        self.assertEqual(len(results), 3)

        # Record 1
        self.assertTrue(results[0].is_valid)
        self.assertEqual(results[0].daily_gdd, 2.0)
        self.assertEqual(results[0].accumulated_gdd, 2.0)

        # Record 2 (Failure)
        self.assertFalse(results[1].is_valid)
        self.assertEqual(results[1].daily_gdd, 0.0)
        self.assertEqual(results[1].accumulated_gdd, 2.0)

        # Record 3 (Recovery)
        self.assertTrue(results[2].is_valid)
        self.assertEqual(results[2].daily_gdd, 6.0)
        self.assertEqual(results[2].accumulated_gdd, 8.0)

    def test_deliberate_wrong_result_cli_exits_nonzero(self):
        """Subprocess test: CLI --scenario failure must exit non-zero with intentional failure message."""
        lab_dir = os.path.dirname(os.path.abspath(__file__))
        example_path = os.path.join(lab_dir, "example.py")

        cmd = [sys.executable, example_path, "--scenario", "failure"]
        proc = subprocess.run(cmd, capture_output=True, text=True)

        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("INTENTIONAL FAILURE", proc.stdout + proc.stderr)

    def test_normal_cli_exits_zero(self):
        """Subprocess test: CLI --scenario normal must exit 0 and output expected total 8.0."""
        lab_dir = os.path.dirname(os.path.abspath(__file__))
        example_path = os.path.join(lab_dir, "example.py")

        cmd = [sys.executable, example_path, "--scenario", "normal"]
        proc = subprocess.run(cmd, capture_output=True, text=True)

        self.assertEqual(proc.returncode, 0, f"Error:\n{proc.stderr}")
        self.assertIn("Final Accumulated GDD: 8.0", proc.stdout)

    def test_boundary_cli_exits_zero(self):
        """Subprocess test: CLI --scenario boundary must exit 0 and verify zero GDD and recovery."""
        lab_dir = os.path.dirname(os.path.abspath(__file__))
        example_path = os.path.join(lab_dir, "example.py")

        cmd = [sys.executable, example_path, "--scenario", "boundary"]
        proc = subprocess.run(cmd, capture_output=True, text=True)

        self.assertEqual(proc.returncode, 0, f"Error:\n{proc.stderr}")
        self.assertIn("ZERO GDD DEMONSTRATIONS", proc.stdout)
        self.assertIn("FAILURE AND RECOVERY STREAM DEMONSTRATION", proc.stdout)


if __name__ == "__main__":
    unittest.main()
