"""A deterministic, hardware-free irrigation hysteresis teaching example.

This is NOT a relay driver, calibration procedure, or physical safety control.
"""

READINGS = (700, 250, 400, 650)


def next_state(watering_on, moisture):
    """Turn on below 300, off above 600; retain state at both thresholds."""
    if type(watering_on) is not bool:
        raise ValueError("watering_on must be a boolean")
    if type(moisture) is not int or not 0 <= moisture <= 1023:
        raise ValueError("moisture must be an integer in 0..1023")
    if moisture < 300:
        return True
    if moisture > 600:
        return False
    return watering_on


def simulate(readings, initial=False):
    state = initial
    states = []
    for reading in readings:
        state = next_state(state, reading)
        states.append("on" if state else "off")
    return states


def main():
    print("FICTIONAL soil readings; no physical pump or relay")
    print("start=off readings=[700, 250, 400, 650]")
    print("states=" + ",".join(simulate(READINGS)))
    print("boundary: 300 with on -> " + ("on" if next_state(True, 300) else "off"))
    print("boundary: 600 with off -> " + ("on" if next_state(False, 600) else "off"))
    try:
        next_state(False, 1024)
    except ValueError as exc:
        print("invalid 1024 -> rejected: " + str(exc))


if __name__ == "__main__":
    main()
