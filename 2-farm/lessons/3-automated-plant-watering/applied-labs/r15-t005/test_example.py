import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from example import (  # noqa: E402
    AutomatedWateringController,
    OfflineRelayAdapter,
    simulate_automated_watering,
    LOWER_THRESHOLD,
    UPPER_THRESHOLD,
    MIN_READING,
    MAX_READING,
)


class TestMoistureControlAdapter(unittest.TestCase):
    def test_sample_sequence(self):
        """Starting off, readings [700,250,400,650] produce [off,on,on,off]."""
        readings = [700, 250, 400, 650]
        expected = ["off", "on", "on", "off"]
        self.assertEqual(simulate_automated_watering(readings, "off"), expected)

    def test_boundary_retention_at_300(self):
        """300 retains previous state whether off or on."""
        adapter = OfflineRelayAdapter("off")
        c = AutomatedWateringController(adapter)
        self.assertEqual(c.process_reading(300), "off")

        # Switch to on
        c.process_reading(200)
        self.assertEqual(c.process_reading(300), "on")

    def test_boundary_retention_at_600(self):
        """600 retains previous state whether on or off."""
        adapter = OfflineRelayAdapter("on")
        c = AutomatedWateringController(adapter)
        self.assertEqual(c.process_reading(600), "on")

        # Switch to off
        c.process_reading(650)
        self.assertEqual(c.process_reading(600), "off")

    def test_actuator_service_command_logging(self):
        """Verify that offline adapter only receives commands on state transitions."""
        adapter = OfflineRelayAdapter("off")
        c = AutomatedWateringController(adapter)
        # Sequence: 700 (off->off no change), 250 (off->on), 400 (on->on no change), 650 (on->off)
        c.process_sequence([700, 250, 400, 650])
        # initial 'off', then transition to 'on', then transition to 'off'
        self.assertEqual(adapter.command_log, ["off", "on", "off"])

    def test_out_of_bounds_rejected(self):
        """Readings outside 0..1023 raise ValueError."""
        adapter = OfflineRelayAdapter("off")
        c = AutomatedWateringController(adapter)
        with self.assertRaises(ValueError):
            c.process_reading(-1)
        with self.assertRaises(ValueError):
            c.process_reading(1024)

    def test_invalid_types_rejected(self):
        """Non-integer types raise TypeError."""
        adapter = OfflineRelayAdapter("off")
        c = AutomatedWateringController(adapter)
        for bad in ["500", 300.5, None, True]:
            with self.assertRaises(TypeError):
                c.process_reading(bad)

    def test_contract_constants(self):
        """Verify thresholds."""
        self.assertEqual(LOWER_THRESHOLD, 300)
        self.assertEqual(UPPER_THRESHOLD, 600)
        self.assertEqual(MIN_READING, 0)
        self.assertEqual(MAX_READING, 1023)


if __name__ == "__main__":
    unittest.main()
