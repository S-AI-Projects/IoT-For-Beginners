import json
from typing import Any, Dict, List


def simulate_hysteresis(
    readings: List[Any],
    low_threshold: int = 300,
    high_threshold: int = 600,
    initial_state: str = "off",
) -> Dict[str, Any]:
    """
    Simulates soil moisture hysteresis control.
    - Switches watering "on" when reading < low_threshold.
    - Switches watering "off" when reading > high_threshold.
    - Retains previous state when low_threshold <= reading <= high_threshold.
    - Rejects readings outside 0..1023 (or non-integers/booleans).
    """
    if initial_state not in ("on", "off"):
        raise ValueError("initial_state must be 'on' or 'off'")
    if not (0 <= low_threshold <= high_threshold <= 1023):
        raise ValueError("Thresholds must satisfy 0 <= low_threshold <= high_threshold <= 1023")

    state = initial_state
    states: List[str] = []
    rejected: List[Dict[str, Any]] = []
    transitions = 0

    for idx, val in enumerate(readings):
        if isinstance(val, bool) or not isinstance(val, int) or not (0 <= val <= 1023):
            rejected.append({
                "index": idx,
                "value": val,
                "reason": "Reading must be an integer within 0..1023",
            })
            continue

        prev_state = state
        if val < low_threshold:
            state = "on"
        elif val > high_threshold:
            state = "off"

        if state != prev_state:
            transitions += 1
        states.append(state)

    return {
        "states": states,
        "rejected": rejected,
        "metrics": {
            "accepted_count": len(states),
            "rejected_count": len(rejected),
            "transitions": transitions,
            "on_ticks": states.count("on"),
        },
    }


def compare_configurations(readings: List[int]) -> List[Dict[str, Any]]:
    """Compares three controlled hysteresis bands on the same noisy reading sequence."""
    configs = [
        {"name": "narrow_band_400_500", "low": 400, "high": 500},
        {"name": "contract_band_300_600", "low": 300, "high": 600},
        {"name": "wide_band_200_700", "low": 200, "high": 700},
    ]
    results = []
    for cfg in configs:
        sim = simulate_hysteresis(readings, low_threshold=cfg["low"], high_threshold=cfg["high"])
        results.append({
            "config": cfg["name"],
            "thresholds": [cfg["low"], cfg["high"]],
            "states": sim["states"],
            "transitions": sim["metrics"]["transitions"],
            "on_ticks": sim["metrics"]["on_ticks"],
        })
    return results


if __name__ == "__main__":
    contract_sample = [700, 250, 400, 650]
    noisy_sequence = [650, 280, 450, 550, 290, 520, 620, 350]
    output = {
        "contract_example": {
            "readings": contract_sample,
            "result": simulate_hysteresis(contract_sample),
        },
        "configuration_comparison": {
            "readings": noisy_sequence,
            "runs": compare_configurations(noisy_sequence),
        },
    }
    print(json.dumps(output, indent=2))
