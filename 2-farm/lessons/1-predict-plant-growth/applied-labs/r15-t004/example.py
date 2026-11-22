"""Growing-degree-day (GDD) calculation — invariant and state trace (R15-T004).

Standard library only. A SIMULATION: does not use physical thermometers or cloud agronomy services.

Contract:
  - Input: daily temperature records (min_temp, max_temp) and base temperature.
  - Formula:
      daily_gdd = max(0.0, ((min_temp + max_temp) / 2.0) - base)
  - Accumulation: total_gdd = sum(daily_gdd)
  - Validation:
      min_temp and max_temp must be numeric.
      Reject records where minimum > maximum (raise ValueError).
  - State Trace & Invariants:
      Maintains intermediate state at each step (day, min, max, mean, daily_gdd, accumulated_gdd).
      Invariant: at step k, accumulated_gdd == sum(trace[i].daily_gdd for i in 0..k).
      Invariant: daily_gdd >= 0.0.
"""


def calculate_daily_gdd(min_temp, max_temp, base_temp):
    """Calculates single-day GDD contribution.

    Raises ValueError if min_temp > max_temp.
    """
    if not isinstance(min_temp, (int, float)) or isinstance(min_temp, bool):
        raise TypeError("Minimum temperature must be numeric")
    if not isinstance(max_temp, (int, float)) or isinstance(max_temp, bool):
        raise TypeError("Maximum temperature must be numeric")
    if not isinstance(base_temp, (int, float)) or isinstance(base_temp, bool):
        raise TypeError("Base temperature must be numeric")

    if min_temp > max_temp:
        raise ValueError(f"Invalid record: minimum temperature {min_temp} > maximum temperature {max_temp}")

    mean_temp = (min_temp + max_temp) / 2.0
    daily_gdd = max(0.0, mean_temp - base_temp)
    return daily_gdd, mean_temp


def calculate_gdd_with_trace(records, base_temp=10.0):
    """Calculates cumulative GDD across a sequence of daily (min, max) records.

    Returns dict containing:
      - 'contributions': list of daily GDD values
      - 'total_gdd': final accumulated GDD
      - 'trace': detailed list of intermediate state steps
    """
    contributions = []
    trace = []
    accumulated = 0.0

    for day_idx, (min_temp, max_temp) in enumerate(records, start=1):
        daily, mean_temp = calculate_daily_gdd(min_temp, max_temp, base_temp)
        accumulated += daily
        contributions.append(daily)

        trace.append({
            "day": day_idx,
            "min_temp": min_temp,
            "max_temp": max_temp,
            "mean_temp": mean_temp,
            "daily_gdd": daily,
            "accumulated_gdd": accumulated,
        })

    return {
        "contributions": contributions,
        "total_gdd": accumulated,
        "trace": trace,
    }


if __name__ == "__main__":
    days = [(8, 16), (12, 20), (2, 8)]
    result = calculate_gdd_with_trace(days, base_temp=10)
    print("Days:", days)
    print("Contributions:", result["contributions"])
    print("Total GDD:    ", result["total_gdd"])
    print("Trace:        ", result["trace"])
