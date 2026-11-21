#!/usr/bin/env python3
"""Growing Degree Days (GDD) calculation with validation and recovery.

Coursework Task: R15-T028
Context: 2-farm/lessons/1-predict-plant-growth

Formula:
  GDD = max(0.0, (minimum + maximum) / 2.0 - base_temperature)
  All temperatures in degrees Celsius (°C).

Educational Scope & Limitations:
  This script is a local mathematical simulation operating on synthetic temperature records.
  It does not connect to real IoT hardware, MQTT brokers, or cloud storage.
  It implements a simplified daily GDD model and does not account for complex
  biological upper temperature cutoffs, photoperiod, or variable diurnal curves.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import math
import sys
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class DailyRecordResult:
    """Represents the processing outcome of a single daily temperature record."""

    day_index: int
    raw_record: Dict[str, Any]
    is_valid: bool
    min_temp: Optional[float] = None
    max_temp: Optional[float] = None
    avg_temp: Optional[float] = None
    daily_gdd: float = 0.0
    accumulated_gdd: float = 0.0
    error_message: Optional[str] = None


def validate_temperature_value(value: Any, param_name: str) -> float:
    """Validate that a temperature value is a finite real number (not a boolean).

    Raises:
      TypeError: If value is a boolean or not int/float.
      ValueError: If value is NaN or infinite.
    """
    if isinstance(value, bool):
        raise TypeError(f"{param_name} cannot be a boolean value ({value!r}).")
    if not isinstance(value, (int, float)):
        raise TypeError(
            f"{param_name} must be a numeric int or float, got {type(value).__name__} ({value!r})."
        )
    try:
        val_float = float(value)
    except OverflowError:
        raise ValueError(
            f"{param_name} is outside the supported numeric range (magnitude too large for float conversion)."
        )
    if math.isnan(val_float) or math.isinf(val_float):
        raise ValueError(f"{param_name} must be a finite number, got {val_float!r}.")
    return val_float


def calculate_daily_gdd(
    min_temp: Any, max_temp: Any, base_temp: Any = 10.0
) -> Tuple[float, float]:
    """Calculate the daily average temperature and daily GDD.

    Args:
      min_temp: Minimum daily temperature in °C.
      max_temp: Maximum daily temperature in °C.
      base_temp: Plant base temperature in °C (default: 10.0°C).

    Returns:
      Tuple of (avg_temp, daily_gdd).

    Raises:
      TypeError: If any input is boolean or non-numeric.
      ValueError: If any input is non-finite or min_temp > max_temp.
    """
    v_min = validate_temperature_value(min_temp, "Minimum temperature")
    v_max = validate_temperature_value(max_temp, "Maximum temperature")
    v_base = validate_temperature_value(base_temp, "Base temperature")

    if v_min > v_max:
        raise ValueError(
            f"Minimum temperature ({v_min}°C) cannot exceed maximum temperature ({v_max}°C)."
        )

    try:
        avg_temp = (v_min + v_max) / 2.0
        daily_gdd = max(0.0, avg_temp - v_base)
    except OverflowError:
        raise ValueError("Temperature calculation overflowed the supported floating-point range.")

    if not math.isfinite(avg_temp) or not math.isfinite(daily_gdd):
        raise ValueError(
            f"Calculated average temperature ({avg_temp}) or daily GDD ({daily_gdd}) is non-finite."
        )

    return avg_temp, daily_gdd


def process_single_record(
    record: Dict[str, Any],
    base_temp: float,
    current_total: float,
    day_index: int,
) -> DailyRecordResult:
    """Validate and process a single day's record, returning the outcome.

    If the record is invalid, returns is_valid=False, daily_gdd=0.0, and
    accumulated_gdd remains unchanged, allowing stream recovery.
    """
    if not isinstance(record, dict):
        return DailyRecordResult(
            day_index=day_index,
            raw_record={"raw": str(record)},
            is_valid=False,
            accumulated_gdd=current_total,
            error_message=f"Record must be a dictionary, got {type(record).__name__}.",
        )

    if "minimum" not in record or record["minimum"] is None:
        return DailyRecordResult(
            day_index=day_index,
            raw_record=record,
            is_valid=False,
            accumulated_gdd=current_total,
            error_message="Missing required 'minimum' temperature field.",
        )

    if "maximum" not in record or record["maximum"] is None:
        return DailyRecordResult(
            day_index=day_index,
            raw_record=record,
            is_valid=False,
            accumulated_gdd=current_total,
            error_message="Missing required 'maximum' temperature field.",
        )

    try:
        avg_temp, gdd = calculate_daily_gdd(
            record["minimum"], record["maximum"], base_temp=base_temp
        )
        new_total = current_total + gdd
        return DailyRecordResult(
            day_index=day_index,
            raw_record=record,
            is_valid=True,
            min_temp=float(record["minimum"]),
            max_temp=float(record["maximum"]),
            avg_temp=avg_temp,
            daily_gdd=gdd,
            accumulated_gdd=new_total,
        )
    except (TypeError, ValueError) as exc:
        return DailyRecordResult(
            day_index=day_index,
            raw_record=record,
            is_valid=False,
            accumulated_gdd=current_total,
            error_message=str(exc),
        )


def process_temperature_records(
    records: List[Dict[str, Any]], base_temp: float = 10.0
) -> List[DailyRecordResult]:
    """Process a sequence of daily temperature records with recovery.

    Invalid records are reported with error messages and contribute 0 GDD.
    Subsequent valid records continue to be processed and accumulated.
    """
    validate_temperature_value(base_temp, "Base temperature")
    results: List[DailyRecordResult] = []
    running_total = 0.0

    for idx, rec in enumerate(records, start=1):
        res = process_single_record(
            rec, base_temp=base_temp, current_total=running_total, day_index=idx
        )
        running_total = res.accumulated_gdd
        results.append(res)

    return results


def run_normal_scenario() -> None:
    """Execute the mandatory normal fixture (3 valid records, base 10°C)."""
    base_temp = 10.0
    records = [
        {"minimum": 8, "maximum": 16},   # Day 1: avg 12 -> GDD 2
        {"minimum": 12, "maximum": 20},  # Day 2: avg 16 -> GDD 6
        {"minimum": 2, "maximum": 8},    # Day 3: avg 5  -> GDD 0
    ]

    print("=" * 80)
    print("Task R15-T028: Growing Degree Days (GDD) Calculation")
    print("Scenario: normal (Mandatory Normal Fixture)")
    print("=" * 80)
    print(f"Base Temperature: {base_temp}°C")
    print(f"Formula: GDD = max(0, (min + max) / 2 - base_temp)")
    print("-" * 80)

    results = process_temperature_records(records, base_temp=base_temp)

    for r in results:
        avg_str = f"{r.avg_temp:.1f}°C" if r.avg_temp is not None else "N/A"
        calc_str = (
            f"max(0, ({r.min_temp} + {r.max_temp})/2 - {base_temp}) = "
            f"max(0, {avg_str} - {base_temp}°C) = {r.daily_gdd:.1f}"
        )
        print(
            f"Day {r.day_index}: min={r.min_temp}°C, max={r.max_temp}°C | "
            f"Avg={avg_str} | Daily GDD={r.daily_gdd:.1f} | "
            f"Accumulated GDD={r.accumulated_gdd:.1f} | Calc: {calc_str}"
        )

    final_total = results[-1].accumulated_gdd
    expected_total = 8.0
    print("-" * 80)
    print(f"Final Accumulated GDD: {final_total:.1f} (Expected: {expected_total:.1f})")

    assert (
        final_total == expected_total
    ), f"Accumulated total mismatch: expected {expected_total}, got {final_total}"
    print("Verification: PASSED (Exact match with expected value 8.0)")
    print("=" * 80)


def run_boundary_scenario() -> None:
    """Execute boundary conditions: average at/below base, missing-data recovery, inverted temps."""
    base_temp = 10.0
    print("=" * 80)
    print("Task R15-T028: Growing Degree Days (GDD) Calculation")
    print("Scenario: boundary (Zero GDD, Inverted Validation, & Failure Recovery)")
    print("=" * 80)

    # 1. Zero GDD Demonstrations
    print("1. ZERO GDD DEMONSTRATIONS (Average at or below base temperature):")
    print("-" * 80)
    zero_cases = [
        {"desc": "Average equal to base (min 10, max 10)", "rec": {"minimum": 10, "maximum": 10}},
        {"desc": "Average equal to base (min 8, max 12)", "rec": {"minimum": 8, "maximum": 12}},
        {"desc": "Average below base (min 2, max 8)", "rec": {"minimum": 2, "maximum": 8}},
        {"desc": "Freezing conditions (min -5, max 1)", "rec": {"minimum": -5, "maximum": 1}},
    ]
    for case in zero_cases:
        avg, gdd = calculate_daily_gdd(case["rec"]["minimum"], case["rec"]["maximum"], base_temp)
        print(f"  {case['desc']}: Avg = {avg:.1f}°C -> GDD = {gdd:.1f} (Expected: 0.0)")
        assert gdd == 0.0, f"Expected 0.0, got {gdd}"
    print("  Verification: PASSED (All non-growth conditions yield exactly 0.0 GDD)")
    print()

    # 2. Inverted Temperature Validation
    print("2. INVERTED TEMPERATURE VALIDATION (Minimum > Maximum):")
    print("-" * 80)
    inverted_rec = {"minimum": 18, "maximum": 14}
    res_inv = process_single_record(inverted_rec, base_temp=base_temp, current_total=0.0, day_index=1)
    print(f"  Input: {inverted_rec}")
    print(f"  Valid: {res_inv.is_valid}")
    print(f"  Error Caught: {res_inv.error_message}")
    assert not res_inv.is_valid
    assert "cannot exceed maximum" in (res_inv.error_message or "")
    print("  Verification: PASSED (Inverted temperatures rejected with descriptive error)")
    print()

    # 3. Failure and Recovery Stream
    print("3. FAILURE AND RECOVERY STREAM DEMONSTRATION:")
    print("-" * 80)
    print("Sequence: [Valid Day 1] -> [Missing 'maximum' Day 2] -> [Valid Day 3]")
    recovery_records = [
        {"minimum": 8, "maximum": 16},  # Day 1: valid, GDD = 2
        {"minimum": 8},                 # Day 2: missing max, rejected
        {"minimum": 12, "maximum": 20}, # Day 3: valid, GDD = 6, recovery!
    ]
    recovery_results = process_temperature_records(recovery_records, base_temp=base_temp)

    for r in recovery_results:
        status_str = "ACCEPTED" if r.is_valid else f"REJECTED ({r.error_message})"
        print(
            f"  Day {r.day_index}: raw={r.raw_record} -> {status_str} | "
            f"Daily GDD={r.daily_gdd:.1f} | Running Total={r.accumulated_gdd:.1f}"
        )

    # Verifications
    assert recovery_results[0].is_valid and recovery_results[0].daily_gdd == 2.0
    assert not recovery_results[1].is_valid and recovery_results[1].daily_gdd == 0.0
    assert recovery_results[1].accumulated_gdd == 2.0  # Total preserved
    assert recovery_results[2].is_valid and recovery_results[2].daily_gdd == 6.0
    assert recovery_results[2].accumulated_gdd == 8.0  # Correct final accumulation

    print()
    print("  Recovery Guarantees Verified:")
    print("    ✓ Record 2 failed due to missing maximum temperature.")
    print("    ✓ Invalid record contributed exactly 0.0 GDD to the accumulated total.")
    print("    ✓ Processing continued seamlessly without terminating.")
    print("    ✓ Record 3 was accepted, reaching the expected final accumulated GDD of 8.0.")
    print("=" * 80)


def run_failure_scenario() -> None:
    """Execute deliberate wrong assertion to demonstrate intentional failure."""
    print("=" * 80)
    print("Task R15-T028: Growing Degree Days (GDD) Calculation")
    print("Scenario: failure (Intentional Failure Demonstration)")
    print("=" * 80)
    print("Notice: This scenario intentionally asserts an incorrect expected GDD total.")
    print("It demonstrates that verification checks properly fail with a non-zero exit code.")
    print()

    records = [
        {"minimum": 8, "maximum": 16},
        {"minimum": 12, "maximum": 20},
        {"minimum": 2, "maximum": 8},
    ]
    results = process_temperature_records(records, base_temp=10.0)
    actual_total = results[-1].accumulated_gdd
    deliberate_false_expected = 999.0

    print(f"Actual Calculated GDD Total: {actual_total:.1f}")
    print(f"False Expected GDD Total:     {deliberate_false_expected:.1f}")
    print()
    print("Triggering deliberate assertion failure now...")
    print("INTENTIONAL FAILURE: Deliberately asserting actual_total == 999.0")

    assert (
        actual_total == deliberate_false_expected
    ), f"INTENTIONAL FAILURE: Actual GDD total ({actual_total:.1f}) != Expected ({deliberate_false_expected:.1f})"


def main() -> None:
    """CLI Entrypoint."""
    parser = argparse.ArgumentParser(
        description="Growing Degree Days (GDD) calculation with validation and recovery."
    )
    parser.add_argument(
        "--scenario",
        default=None,
        choices=["normal", "boundary", "failure"],
        help="CLI scenario: 'normal', 'boundary', or 'failure'.",
    )
    parser.add_argument(
        "positional_scenario",
        nargs="?",
        default=None,
        choices=["normal", "boundary", "failure"],
        help="Optional positional scenario name.",
    )

    args = parser.parse_args()
    scenario = args.scenario or args.positional_scenario or "normal"

    if scenario == "normal":
        run_normal_scenario()
    elif scenario == "boundary":
        run_boundary_scenario()
    elif scenario == "failure":
        run_failure_scenario()


if __name__ == "__main__":
    main()
