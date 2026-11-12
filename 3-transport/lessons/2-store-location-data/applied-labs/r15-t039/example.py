"""Geofence scenario assessment (R15-T039).

Standard library only. A SIMULATION on local data. The geofence is a flat
latitude/longitude rectangle, NOT a spherical-distance (great-circle) model.

Coordinate order is (latitude, longitude). The fence is latitude [10, 20],
longitude [70, 80]. The default boundary policy is "inclusive" (both ends
count as inside). Invalid input raises ValueError.

The module holds three applied questions (predict, diagnose, choose a policy).
Each has a stated answer, a rationale and an executable check that COMPUTES
the answer, so the stated answer cannot drift from the code.
"""

LAT_MIN, LAT_MAX = 10, 20
LON_MIN, LON_MAX = 70, 80
POLICIES = ("inclusive", "half_open")


def _number(name, v):
    if isinstance(v, bool) or not isinstance(v, (int, float)) or v != v:
        raise ValueError("%s must be a number, got %r" % (name, v))


def classify(lat, lon, policy="inclusive", fence=(LAT_MIN, LAT_MAX, LON_MIN, LON_MAX)):
    """Return 'inside' or 'outside'; raise ValueError for invalid input.

    policy 'inclusive': lower and upper bounds both count as inside.
    policy 'half_open': lower bound inside, upper bound outside.
    """
    if policy not in POLICIES:
        raise ValueError("unknown policy %r" % (policy,))
    _number("latitude", lat)
    _number("longitude", lon)
    if not -90 <= lat <= 90:
        raise ValueError("latitude %r is outside -90..90" % (lat,))
    if not -180 <= lon <= 180:
        raise ValueError("longitude %r is outside -180..180" % (lon,))
    la0, la1, lo0, lo1 = fence
    if policy == "inclusive":
        inside = la0 <= lat <= la1 and lo0 <= lon <= lo1
    else:
        inside = la0 <= lat < la1 and lo0 <= lon < lo1
    return "inside" if inside else "outside"


def diagnose(lat, lon, expected):
    """Explain why a record was not classified as expected.
    Returns a short diagnosis string, or 'ok' if it matches."""
    try:
        actual = classify(lat, lon)
    except ValueError as err:
        return "rejected: %s" % err
    if actual == expected:
        return "ok"
    try:
        if classify(lon, lat) == expected:
            return "coordinate order swapped: (%s, %s) is (longitude, latitude)" % (lat, lon)
    except ValueError:
        pass
    return "genuinely %s the fence" % actual


# ---- the three applied questions -------------------------------------------
RECORDS = [(15, 75), (10, 70), (21, 75)]
ADJACENT = (20, 30, 70, 80)   # a second fence that shares the latitude-20 edge


def _q1():
    return [classify(*r) for r in RECORDS]


def _q2():
    return diagnose(75, 15, "inside")


def _q3():
    edge = (20, 75)
    return {
        "inclusive": [classify(*edge) == "inside",
                      classify(*edge, fence=ADJACENT) == "inside"].count(True),
        "half_open": [classify(*edge, policy="half_open") == "inside",
                      classify(*edge, policy="half_open", fence=ADJACENT) == "inside"].count(True),
    }


QUESTIONS = [
    {
        "id": "Q1 predict",
        "question": "What does classify return for (15, 75), (10, 70) and (21, 75)?",
        "answer": ["inside", "inside", "outside"],
        "rationale": "(15, 75) is inside both ranges; (10, 70) sits exactly on the lower "
                     "bounds and the policy is inclusive; 21 is above the latitude limit of 20.",
        "check": _q1,
    },
    {
        "id": "Q2 diagnose",
        "question": "A tracker reports (75, 15) for a vehicle known to be inside the fence, "
                    "but it is classified outside. Why?",
        "answer": "coordinate order swapped: (75, 15) is (longitude, latitude)",
        "rationale": "The fence expects (latitude, longitude). (75, 15) is read as latitude 75, "
                     "which is outside 10..20. Swapping gives (15, 75), which is inside.",
        "check": _q2,
    },
    {
        "id": "Q3 policy",
        "question": "Two fences share the latitude-20 edge. How many fences contain the edge "
                    "point (20, 75) under each boundary policy?",
        "answer": {"inclusive": 2, "half_open": 1},
        "rationale": "Inclusive counts the shared edge in both fences, so a vehicle on it is "
                     "in two fences at once. Half-open gives each edge point to exactly one "
                     "fence. This lesson uses inclusive because its stated rule is that "
                     "boundary points are inside; the cost is the double count.",
        "check": _q3,
    },
]


def run_checks():
    """Return a list of (id, stated_answer, computed_answer, matches)."""
    out = []
    for q in QUESTIONS:
        computed = q["check"]()
        out.append((q["id"], q["answer"], computed, computed == q["answer"]))
    return out


if __name__ == "__main__":
    for qid, stated, computed, ok in run_checks():
        print("%s: %s" % (qid, "OK" if ok else "MISMATCH"))
        print("   stated:   ", stated)
        print("   computed: ", computed)
