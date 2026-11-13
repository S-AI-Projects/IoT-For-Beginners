import json
import math
from typing import Any

LAT_MIN, LAT_MAX = 10.0, 20.0
LON_MIN, LON_MAX = 70.0, 80.0


def _validate_coordinate(lat: Any, lon: Any) -> tuple[float, float]:
    """Validate geographic bounds: latitude in [-90, 90], longitude in [-180, 180]."""
    if isinstance(lat, bool) or not isinstance(lat, (int, float)) or not math.isfinite(lat):
        raise ValueError(f"Invalid latitude {lat!r}: must be a finite number.")
    if isinstance(lon, bool) or not isinstance(lon, (int, float)) or not math.isfinite(lon):
        raise ValueError(f"Invalid longitude {lon!r}: must be a finite number.")
    if not (-90.0 <= lat <= 90.0):
        raise ValueError(f"Latitude {lat} out of valid range [-90, 90].")
    if not (-180.0 <= lon <= 180.0):
        raise ValueError(f"Longitude {lon} out of valid range [-180, 180].")
    return float(lat), float(lon)


def evaluate_geofence_with_trace(records: list[dict[str, Any]]) -> dict[str, Any]:
    """
    Classify local coordinate records against an inclusive rectangular teaching
    geofence (lat in [10, 20], lon in [70, 80]) while recording intermediate state
    at each pipeline step.
    Note: This rectangular fixture is NOT a spherical-distance model.
    """
    state_trace: list[dict[str, Any]] = []
    results: list[dict[str, Any]] = []

    for step_idx, record in enumerate(records):
        if "lat" not in record or "lon" not in record:
            raise ValueError(f"Record missing 'lat' or 'lon': {record!r}")

        rec_id = record.get("id", f"rec-{step_idx}")
        lat, lon = _validate_coordinate(record["lat"], record["lon"])

        lat_in_bounds = LAT_MIN <= lat <= LAT_MAX
        lon_in_bounds = LON_MIN <= lon <= LON_MAX
        inside = lat_in_bounds and lon_in_bounds

        state_trace.append({
            "step": step_idx,
            "id": rec_id,
            "validated_lat": lat,
            "validated_lon": lon,
            "lat_in_bounds": lat_in_bounds,
            "lon_in_bounds": lon_in_bounds,
            "computed_inside": inside,
        })

        results.append({
            "id": rec_id,
            "lat": lat,
            "lon": lon,
            "inside": inside,
        })

    return {
        "model": "inclusive-rectangular-fixture (not spherical-distance)",
        "bounds": {"lat": [LAT_MIN, LAT_MAX], "lon": [LON_MIN, LON_MAX]},
        "state_trace": state_trace,
        "results": results,
    }


if __name__ == "__main__":
    sample_records = [
        {"id": "interior", "lat": 15, "lon": 75},
        {"id": "boundary", "lat": 10, "lon": 70},
        {"id": "outside", "lat": 21, "lon": 75},
    ]
    print(json.dumps(evaluate_geofence_with_trace(sample_records), indent=2))
