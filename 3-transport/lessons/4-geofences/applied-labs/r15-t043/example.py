"""Inclusive rectangular geofence for local teaching data, not spherical distance."""
import math

# Input order is (latitude, longitude), not GeoJSON's (longitude, latitude).
SAMPLES = ((15, 75, "inside"), (10, 70, "inside"), (21, 75, "outside"))


def classify(latitude, longitude):
    """Return inside/outside; reject impossible or non-finite coordinates."""
    for name, value, low, high in (("latitude", latitude, -90, 90),
                                   ("longitude", longitude, -180, 180)):
        if type(value) not in (int, float) or not math.isfinite(value) or not low <= value <= high:
            raise ValueError("invalid " + name)
    return "inside" if 10 <= latitude <= 20 and 70 <= longitude <= 80 else "outside"


def compare_expected():
    """Independent, hand-authored expected-result table for the same inputs."""
    return [(lat, lon, expected, classify(lat, lon)) for lat, lon, expected in SAMPLES]


def main():
    print("FICTIONAL rectangle: latitude [10,20], longitude [70,80]; inclusive")
    for lat, lon, expected, actual in compare_expected():
        print("({},{}): expected={} actual={}".format(lat, lon, expected, actual))
    try:
        classify(100, 75)
    except ValueError as exc:
        print("(100,75): rejected: " + str(exc))
    print("Not a spherical-distance model, GPS feed or Azure Maps query.")


if __name__ == "__main__":
    main()
