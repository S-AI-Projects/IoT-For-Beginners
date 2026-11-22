import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from example import (  # noqa: E402
    MoistureController,
    simulate_moisture_control,
    LOWER_THRESHOLD,
    UPPER_THRESHOLD,
    MIN_READING,
    MAX_READING,
)


class TestMoistureHysteresis(unittest.TestCase):
    def test_sample_sequence(self):
        """Starting off, readings [700,250,400,650] produce [off,on,on,off]."""
        readings = [700, 250, 400, 650]
        expected = ["off", "on", "on", "off"]
        self.assertEqual(simulate_moisture_control(readings, initial_state="off"), expected)

    def test_boundary_retention_at_300(self):
        """300 retains previous state whether off or on."""
        # When starting off, 300 stays off
        c1 = MoistureController("off")
        self.assertEqual(c1.process_reading(300), "off")

        # When on, 300 stays on
        c2 = MoistureController("off")
        c2.process_reading(250)  # turns on
        self.assertEqual(c2.process_reading(300), "on")

    def test_boundary_retention_at_600(self):
        """600 retains previous state whether on or off."""
        # When on, 600 stays on
        c1 = MoistureController("on")
        self.assertEqual(c1.process_reading(600), "on")

        # When off, 600 stays off
        c2 = MoistureController("off")
        self.assertEqual(c2.process_reading(600), "off")

    def test_threshold_switching(self):
        """Reading 299 turns on; reading 601 turns off."""
        c = MoistureController("off")
        self.assertEqual(c.process_reading(299), "on")
        self.assertEqual(c.process_reading(601), "off")

    def test_valid_extremes(self):
        """Sensor extremes 0 and 1023 are valid."""
        c = MoistureController("off")
        self.assertEqual(c.process_reading(MIN_READING), "on")
        self.assertEqual(c.process_reading(MAX_READING), "off")

    def test_out_of_bounds_rejected(self):
        """Readings outside 0..1023 raise ValueError."""
        c = MoistureController("off")
        with self.assertRaises(ValueError):
            c.process_reading(-1)
        with self.assertRaises(ValueError):
            c.process_reading(1024)

    def test_invalid_types_rejected(self):
        """Non-integer types raise TypeError."""
        c = MoistureController("off")
        for bad in ["400", 350.5, None, True]:
            with self.assertRaises(TypeError):
                c.process_reading(bad)

    def test_concept_mapping(self):
        """Verify thresholds match lesson specifications."""
        self.assertEqual(LOWER_THRESHOLD, 300)
        self.assertEqual(UPPER_THRESHOLD, 600)
        self.assertEqual(MIN_READING, 0)
        self.assertEqual(MAX_READING, 1023)


if __name__ == "__main__":
    unittest.main()
