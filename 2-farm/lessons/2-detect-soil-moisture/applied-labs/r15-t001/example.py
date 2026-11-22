"""Moisture-control hysteresis (R15-T001).

Standard library only. A SIMULATION: it does not interact with physical soil
moisture sensors or relays. It illustrates how an IoT controller prevents
rapid actuator oscillation (chattering) by applying hysteresis thresholds.

Rules:
  - Input: integer soil moisture reading in range 0..1023.
  - Readings below 300 turn watering ON.
  - Readings above 600 turn watering OFF.
  - Readings between 300 and 600 (inclusive) retain the previous watering state.
  - Initial state defaults to 'off'.
  - Readings outside 0..1023 are rejected with ValueError.
"""

# Thresholds mapped to lesson concepts
LOWER_THRESHOLD = 300  # Below this, soil is dry; turn watering on
UPPER_THRESHOLD = 600  # Above this, soil is wet; turn watering off
MIN_READING = 0
MAX_READING = 1023


class MoistureController:
    """Maintains actuator state across consecutive moisture readings."""

    def __init__(self, initial_state="off"):
        if initial_state not in ("off", "on"):
            raise ValueError(f"Invalid initial state: {initial_state}")
        self.state = initial_state

    def process_reading(self, reading):
        """Processes a single reading and returns updated state ('on' or 'off')."""
        if not isinstance(reading, int) or isinstance(reading, bool):
            raise TypeError("Reading must be an integer")
        if reading < MIN_READING or reading > MAX_READING:
            raise ValueError(f"Reading {reading} outside valid sensor range [0, 1023]")

        if reading < LOWER_THRESHOLD:
            self.state = "on"
        elif reading > UPPER_THRESHOLD:
            self.state = "off"
        # At 300 and 600, or in between, retain existing self.state

        return self.state

    def process_sequence(self, readings):
        """Processes a sequence of readings and returns list of states."""
        return [self.process_reading(r) for r in readings]


def simulate_moisture_control(readings, initial_state="off"):
    """Convenience function to simulate a sequence of moisture readings."""
    controller = MoistureController(initial_state)
    return controller.process_sequence(readings)


if __name__ == "__main__":
    sample = [700, 250, 400, 650]
    print("Readings:", sample)
    print("States:  ", simulate_moisture_control(sample))
