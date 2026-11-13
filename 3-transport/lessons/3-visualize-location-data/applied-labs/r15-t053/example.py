import json
import math
from typing import Any, Callable

LAT_MIN, LAT_MAX = 10.0, 20.0
LON_MIN, LON_MAX = 70.0, 80.0

GeofenceAdapter = Callable[[float, float], bool]


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


def local_rectangular_geofence_adapter(lat: float, lon: float) -> bool:
    """
    Deterministic offline adapter implementing an inclusive rectangular
    teaching geofence: latitude in [10, 20] and longitude in [70, 80].
    Note: This is an axis-aligned rectangular fixture, NOT a spherical-distance model.
    """
    return (LAT_MIN <= lat <= LAT_MAX) and (LON_MIN <= lon <= LON_MAX)


def classify_coordinates(
    records: list[dict[str, Any]],
    adapter: GeofenceAdapter = local_rectangular_geofence_adapter,
) -> list[dict[str, Any]]:
    """Classify local coordinate records through the injected geofence adapter."""
    results: list[dict[str, Any]] = []
    for record in records:
        if "lat" not in record or "lon" not in record:
            raise ValueError(f"Record missing 'lat' or 'lon': {record!r}")
        lat, lon = _validate_coordinate(record["lat"], record["lon"])
        inside = bool(adapter(lat, lon))
        results.append({
            "id": record.get("id", "unknown"),
            "lat": lat,
            "lon": lon,
            "inside": inside,
        })
    return results


if __name__ == "__main__":
    sample_records = [
        {"id": "interior", "lat": 15, "lon": 75},
        {"id": "boundary", "lat": 10, "lon": 70},
        {"id": "outside", "lat": 21, "lon": 75},
    ]
    output = {
        "model": "inclusive-rectangular-fixture (not spherical-distance)",
        "bounds": {"lat": [LAT_MIN, LAT_MAX], "lon": [LON_MIN, LON_MAX]},
        "results": classify_coordinates(sample_records),
    }
    print(json.dumps(output, indent=2))
