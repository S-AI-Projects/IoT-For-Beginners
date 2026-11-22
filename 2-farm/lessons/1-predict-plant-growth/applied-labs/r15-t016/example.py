"""
Growing-Degree Calculation — Refactor the Teaching Example (R15-T016)

Lesson reference: 2-farm/lessons/1-predict-plant-growth/README.md
Concept: Growing Degree Days (GDD) measure heat accumulation to predict plant development stages.
Formula:
    daily_gdd = max(0, ((minimum + maximum) / 2) - base)
Accumulated GDD is the sum of daily contributions across a date range.

Contract:
1. Daily temperatures (minimum, maximum) must be numeric.
2. Reject minimum > maximum with ValueError.
3. Compute daily GDD with respect to a base threshold (e.g. 10).
4. Refactoring focus: Provide an initial monolithic baseline and an extracted single-responsibility
   function, proving behavioral equivalence.
"""

from typing import List, Tuple


# --- Baseline Monolithic Implementation ---
def calculate_gdd_baseline(
    temperature_records: List[Tuple[float, float]], base_temperature: float = 10.0
) -> Tuple[List[float], float]:
    """
    Baseline implementation: combines input validation, daily calculation,
    and accumulation in a single monolithic loop.
    """
    contributions = []
    total = 0.0
    for min_temp, max_temp in temperature_records:
        if isinstance(min_temp, bool) or isinstance(max_temp, bool) or not isinstance(min_temp, (int, float)) or not isinstance(max_temp, (int, float)):
            raise TypeError("Temperatures must be numeric")
        if min_temp > max_temp:
            raise ValueError(f"Invalid record: minimum temperature ({min_temp}) exceeds maximum temperature ({max_temp})")
        mean_temp = (min_temp + max_temp) / 2.0
        daily = max(0.0, mean_temp - base_temperature)
        contributions.append(daily)
        total += daily
    return contributions, total


# --- Refactored Implementation (Extracted Responsibility) ---
def compute_single_day_gdd(min_temp: float, max_temp: float, base_temperature: float) -> float:
    """
    Extracted named responsibility: Validates a single daily record and computes
    its individual GDD contribution.
    """
    if isinstance(min_temp, bool) or isinstance(max_temp, bool) or not isinstance(min_temp, (int, float)) or not isinstance(max_temp, (int, float)):
        raise TypeError("Temperatures must be numeric")
    if min_temp > max_temp:
        raise ValueError(f"Invalid record: minimum temperature ({min_temp}) exceeds maximum temperature ({max_temp})")

    mean_temp = (min_temp + max_temp) / 2.0
    return max(0.0, mean_temp - base_temperature)


def calculate_gdd_refactored(
    temperature_records: List[Tuple[float, float]], base_temperature: float = 10.0
) -> Tuple[List[float], float]:
    """
    Refactored implementation: delegates daily computation to compute_single_day_gdd
    and handles accumulation cleanly.
    """
    contributions = [compute_single_day_gdd(mn, mx, base_temperature) for mn, mx in temperature_records]
    total = sum(contributions)
    return contributions, total


def run_demo():
    fixture = [(8, 16), (12, 20), (2, 8)]
    base = 10.0
    contribs, total = calculate_gdd_refactored(fixture, base)
    print(f"Fixture: {fixture}, Base: {base}")
    print(f"Daily contributions: {contribs}")
    print(f"Total accumulated GDD: {total}")
    return contribs, total


if __name__ == "__main__":
    run_demo()
