"""Tests for the hardware-free moisture hysteresis example."""
import os
import unittest
from example import READINGS, next_state, simulate


class HysteresisTests(unittest.TestCase):
    def test_required_fixture(self):
        self.assertEqual(simulate(READINGS), ["off", "on", "on", "off"])

    def test_thresholds_retain_both_states(self):
        for threshold in (300, 600):
            self.assertTrue(next_state(True, threshold))
            self.assertFalse(next_state(False, threshold))

    def test_range_endpoints(self):
        self.assertTrue(next_state(False, 0))
        self.assertFalse(next_state(True, 1023))

    def test_invalid_readings(self):
        for value in (-1, 1024, 299.5, "250", True, None):
            with self.subTest(value=value), self.assertRaises(ValueError):
                next_state(False, value)

    def test_invalid_initial_state(self):
        with self.assertRaises(ValueError):
            next_state("off", 400)

    @unittest.skipUnless(os.getenv("RUN_INTENTIONAL_FAILURE") == "1", "negative test runs separately")
    def test_deliberately_wrong_result_fails(self):
        self.assertEqual(simulate(READINGS), ["on", "on", "on", "on"])


if __name__ == "__main__":
    unittest.main()
