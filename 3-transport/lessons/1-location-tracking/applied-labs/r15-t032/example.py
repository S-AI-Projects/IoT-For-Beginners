"""Rectangular teaching geofence (R15-T032).

Standard library only. A SIMULATION on local data: the geofence is a flat
latitude/longitude rectangle, NOT a spherical-distance (great-circle) model.

Coordinate order is (latitude, longitude). Bounds are inclusive:
latitude in [10, 20], longitude in [70, 80].
Valid ranges: latitude -90..90, longitude -180..180; anything else is invalid.
"""

LAT_MIN, LAT_MAX = 10, 20
LON_MIN, LON_MAX = 70, 80


def classify(lat, lon):
    """Direct implementation. Returns 'inside', 'outside' or 'invalid'."""
    for v in (lat, lon):
        if isinstance(v, bool) or not isinstance(v, (int, float)) or v != v:
            return "invalid"
    if not -90 <= lat <= 90 or not -180 <= lon <= 180:
        return "invalid"
    if LAT_MIN <= lat <= LAT_MAX and LON_MIN <= lon <= LON_MAX:
        return "inside"
    return "outside"


def classify_by_clamp(lat, lon):
    """Independent calculation: a point is inside when clamping it to the
    rectangle leaves it unchanged. Uses min/max instead of comparisons."""
    for v in (lat, lon):
        if isinstance(v, bool) or not isinstance(v, (int, float)) or v != v:
            return "invalid"
    if abs(lat) > 90 or abs(lon) > 180:
        return "invalid"
    clamped = (min(max(lat, LAT_MIN), LAT_MAX), min(max(lon, LON_MIN), LON_MAX))
    return "inside" if clamped == (lat, lon) else "outside"


# Explicit expected-result table: (lat, lon) -> expected
EXPECTED = {
    (15, 75): "inside",
    (10, 70): "inside",    # lower-left corner, boundary is inclusive
    (20, 80): "inside",    # upper-right corner
    (21, 75): "outside",   # just above the latitude bound
    (15, 69.999): "outside",
    (100, 75): "invalid",  # latitude out of range
    (15, 181): "invalid",  # longitude out of range
}


if __name__ == "__main__":
    for point, expected in EXPECTED.items():
        print(point, classify(*point), classify_by_clamp(*point), expected)
