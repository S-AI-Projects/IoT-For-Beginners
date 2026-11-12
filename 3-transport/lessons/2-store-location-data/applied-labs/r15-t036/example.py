"""Worked geofence example for stored location records (R15-T036).

Standard library only. A SIMULATION on local data. The geofence is a flat
latitude/longitude rectangle, NOT a spherical-distance (great-circle) model.

Coordinate order is (latitude, longitude). Bounds are inclusive:
latitude in [10, 20], longitude in [70, 80].
Invalid input (latitude outside -90..90, longitude outside -180..180, or not
a number) is rejected by raising ValueError.
"""

LAT_MIN, LAT_MAX = 10, 20
LON_MIN, LON_MAX = 70, 80


def _check_number(name, value):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or value != value:
        raise ValueError("%s must be a number, got %r" % (name, value))


def classify(lat, lon):
    """Return 'inside' or 'outside'. Raise ValueError for invalid input."""
    _check_number("latitude", lat)
    _check_number("longitude", lon)
    if not -90 <= lat <= 90:
        raise ValueError("latitude %r is outside -90..90" % (lat,))
    if not -180 <= lon <= 180:
        raise ValueError("longitude %r is outside -180..180" % (lon,))
    lat_ok = LAT_MIN <= lat <= LAT_MAX
    lon_ok = LON_MIN <= lon <= LON_MAX
    return "inside" if lat_ok and lon_ok else "outside"


def explain(lat, lon):
    """Worked input-to-output explanation: one line per step."""
    lines = ["input: latitude=%s, longitude=%s" % (lat, lon)]
    try:
        result = classify(lat, lon)
    except ValueError as err:
        lines.append("rejected: %s" % err)
        lines.append("result: invalid")
        return lines
    lines.append("latitude %s in [%s, %s]: %s"
                 % (lat, LAT_MIN, LAT_MAX, LAT_MIN <= lat <= LAT_MAX))
    lines.append("longitude %s in [%s, %s]: %s"
                 % (lon, LON_MIN, LON_MAX, LON_MIN <= lon <= LON_MAX))
    lines.append("result: %s" % result)
    return lines


# The worked examples: (lat, lon) -> expected explanation lines.
WORKED = {
    (15, 75): [
        "input: latitude=15, longitude=75",
        "latitude 15 in [10, 20]: True",
        "longitude 75 in [70, 80]: True",
        "result: inside",
    ],
    (10, 70): [
        "input: latitude=10, longitude=70",
        "latitude 10 in [10, 20]: True",
        "longitude 70 in [70, 80]: True",
        "result: inside",
    ],
    (21, 75): [
        "input: latitude=21, longitude=75",
        "latitude 21 in [10, 20]: False",
        "longitude 75 in [70, 80]: True",
        "result: outside",
    ],
    (100, 75): [
        "input: latitude=100, longitude=75",
        "rejected: latitude 100 is outside -90..90",
        "result: invalid",
    ],
}


if __name__ == "__main__":
    for point in WORKED:
        print("\n".join(explain(*point)))
        print()
