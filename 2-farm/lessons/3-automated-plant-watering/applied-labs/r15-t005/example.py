"""Moisture-control hysteresis — offline service adapter (R15-T005).

Standard library only. A SIMULATION: does not use physical relays, GPIO pins,
pumps, or network MQTT/cloud services.

Focus:
  Puts external actuator control behind a callable interface (RelayActuatorService)
  and provides a deterministic local offline adapter (OfflineRelayAdapter).

Hysteresis rules:
  - Input: integer moisture readings in range 0..1023.
  - Readings below 300 switch watering 'on'.
  - Readings above 600 switch watering 'off'.
  - Readings between 300 and 600 retain the previous state.
  - Starting state defaults to 'off'.
  - Readings outside 0..1023 are rejected with ValueError.
  - Sequence [700, 250, 400, 650] produces ['off', 'on', 'on', 'off'].

Real-service behavior this mock does NOT establish:
  1. Mechanical relay contact bounce, mechanical wear, or coil energization latency.
  2. Network transport latency, socket disconnection, or MQTT packet drop.
  3. Water reservoir depletion, pump motor overheating, or hydraulic plumbing pressure drop.
  4. Physical sensor latency (time taken for water to diffuse through soil to the probe).
"""

LOWER_THRESHOLD = 300
UPPER_THRESHOLD = 600
MIN_READING = 0
MAX_READING = 1023


class RelayActuatorService:
    """Callable interface contract for watering actuator."""

    def set_watering(self, state: str) -> None:
        raise NotImplementedError

    def get_state(self) -> str:
        raise NotImplementedError


class OfflineRelayAdapter(RelayActuatorService):
    """Deterministic in-memory offline adapter implementing the actuator interface."""

    def __init__(self, initial_state: str = "off"):
        if initial_state not in ("off", "on"):
            raise ValueError(f"Invalid initial state: {initial_state}")
        self._state = initial_state
        self.command_log = [initial_state]

    def set_watering(self, state: str) -> None:
        if state not in ("off", "on"):
            raise ValueError(f"Invalid actuator command: {state}")
        self._state = state
        self.command_log.append(state)

    def get_state(self) -> str:
        return self._state


class AutomatedWateringController:
    """Controller using the external actuator service adapter."""

    def __init__(self, actuator: RelayActuatorService):
        self.actuator = actuator

    def process_reading(self, reading: int) -> str:
        """Processes a single reading and commands the actuator service."""
        if not isinstance(reading, int) or isinstance(reading, bool):
            raise TypeError("Reading must be an integer")
        if reading < MIN_READING or reading > MAX_READING:
            raise ValueError(f"Reading {reading} outside valid sensor range [0, 1023]")

        current_state = self.actuator.get_state()
        if reading < LOWER_THRESHOLD:
            new_state = "on"
        elif reading > UPPER_THRESHOLD:
            new_state = "off"
        else:
            new_state = current_state  # 300 and 600 retain previous state

        if new_state != current_state:
            self.actuator.set_watering(new_state)

        return self.actuator.get_state()

    def process_sequence(self, readings: list) -> list:
        """Processes a sequence of readings and returns the resulting states."""
        return [self.process_reading(r) for r in readings]


def simulate_automated_watering(readings: list, initial_state: str = "off") -> list:
    """Convenience simulation helper."""
    adapter = OfflineRelayAdapter(initial_state)
    controller = AutomatedWateringController(adapter)
    return controller.process_sequence(readings)


if __name__ == "__main__":
    sample = [700, 250, 400, 650]
    adapter = OfflineRelayAdapter("off")
    controller = AutomatedWateringController(adapter)
    states = controller.process_sequence(sample)
    print("Readings:     ", sample)
    print("States:       ", states)
    print("Actuator log: ", adapter.command_log)
