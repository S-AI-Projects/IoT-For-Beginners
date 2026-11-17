"""Unit tests for Sensor-Message Validation Example (Task R15-T022).

Uses Python's standard library unittest framework to verify schema validation,
boundary conditions (zero readings, non-numerics), deduplication, and
deterministic chronological sorting.
"""

import os
import sys
import unittest

# Ensure the module directory is accessible for direct execution or discovery
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from example import (  # noqa: E402
    get_required_fixture,
    process_sensor_messages,
    validate_sensor_message,
)


class TestSensorMessageValidation(unittest.TestCase):
    """Test suite for sensor telemetry validation, deduplication, and ordering."""

    # 1. Valid messages
    def test_valid_message(self) -> None:
        """Test that a well-formed message passes validation without error."""
        valid_msg = {"device_id": "sensor-01", "timestamp": 1000.5, "reading": 23.4}
        try:
            validate_sensor_message(valid_msg)
        except Exception as exc:
            self.fail(f"validate_sensor_message raised an unexpected exception: {exc}")

    # 2. Timestamp ordering
    def test_timestamp_ordering(self) -> None:
        """Test that accepted messages are returned sorted ascending by timestamp."""
        unordered = [
            {"device_id": "Device-A", "timestamp": 50, "reading": 10.0},
            {"device_id": "Device-A", "timestamp": 10, "reading": 12.0},
            {"device_id": "Device-A", "timestamp": 30, "reading": 11.0},
        ]
        result = process_sensor_messages(unordered)
        self.assertEqual(len(result.accepted), 3)
        timestamps = [m["timestamp"] for m in result.accepted]
        self.assertEqual(timestamps, [10, 30, 50])

    # 3. Duplicate device/timestamp pairs
    def test_duplicate_device_timestamp_pairs(self) -> None:
        """Test that identical (device_id, timestamp) pairs are flagged as duplicates."""
        messages = [
            {"device_id": "Device-A", "timestamp": 100, "reading": 20.0},
            {"device_id": "Device-A", "timestamp": 100, "reading": 25.5},  # duplicate
        ]
        result = process_sensor_messages(messages)
        self.assertEqual(len(result.accepted), 1)
        self.assertEqual(
            result.accepted[0]["reading"], 20.0, "First occurrence must be kept"
        )
        self.assertEqual(len(result.duplicates), 1)
        self.assertEqual(result.duplicates[0]["message"]["reading"], 25.5)
        self.assertEqual(len(result.invalid), 0)

    # 4. Same timestamp belonging to different devices
    def test_same_timestamp_different_devices(self) -> None:
        """Test that the same timestamp on different devices is NOT considered a duplicate."""
        messages = [
            {"device_id": "Device-B", "timestamp": 200, "reading": 15.0},
            {"device_id": "Device-A", "timestamp": 200, "reading": 10.0},
        ]
        result = process_sensor_messages(messages)
        self.assertEqual(len(result.accepted), 2, "Both devices should be accepted")
        self.assertEqual(len(result.duplicates), 0)
        # Deterministic sort check: Device-A should sort before Device-B
        self.assertEqual(result.accepted[0]["device_id"], "Device-A")
        self.assertEqual(result.accepted[1]["device_id"], "Device-B")

    # 5. Zero reading (boundary case)
    def test_zero_reading_accepted(self) -> None:
        """Test that zero readings (0, 0.0) are valid numeric measurements."""
        zero_int = {"device_id": "Device-A", "timestamp": 1, "reading": 0}
        zero_float = {"device_id": "Device-B", "timestamp": 2, "reading": 0.0}

        # Must not raise validation errors
        validate_sensor_message(zero_int)
        validate_sensor_message(zero_float)

        result = process_sensor_messages([zero_int, zero_float])
        self.assertEqual(len(result.accepted), 2)
        self.assertEqual(result.accepted[0]["reading"], 0)
        self.assertEqual(result.accepted[1]["reading"], 0.0)

    # 6. String reading rejection
    def test_string_reading_rejection(self) -> None:
        """Test that string readings like '25.5' are rejected as invalid types."""
        str_reading = {"device_id": "Device-A", "timestamp": 1, "reading": "25.5"}
        with self.assertRaises(TypeError):
            validate_sensor_message(str_reading)

        result = process_sensor_messages([str_reading])
        self.assertEqual(len(result.accepted), 0)
        self.assertEqual(len(result.invalid), 1)
        self.assertIn("reading", result.invalid[0]["reason"].lower())

    # 7. Boolean reading rejection
    def test_boolean_reading_rejection(self) -> None:
        """Test that boolean values for readings are rejected, avoiding bool-as-int bugs."""
        bool_true = {"device_id": "Device-A", "timestamp": 1, "reading": True}
        bool_false = {"device_id": "Device-A", "timestamp": 2, "reading": False}

        with self.assertRaises(TypeError):
            validate_sensor_message(bool_true)
        with self.assertRaises(TypeError):
            validate_sensor_message(bool_false)

        result = process_sensor_messages([bool_true, bool_false])
        self.assertEqual(len(result.accepted), 0)
        self.assertEqual(len(result.invalid), 2)

    # 8. NaN and infinity rejection
    def test_nan_and_infinity_rejection(self) -> None:
        """Test that non-finite floats (NaN, Inf, -Inf) are rejected for readings and timestamps."""
        nan_reading = {
            "device_id": "Device-A",
            "timestamp": 1,
            "reading": float("nan"),
        }
        inf_reading = {
            "device_id": "Device-A",
            "timestamp": 1,
            "reading": float("inf"),
        }
        neginf_reading = {
            "device_id": "Device-A",
            "timestamp": 1,
            "reading": float("-inf"),
        }
        nan_ts = {
            "device_id": "Device-A",
            "timestamp": float("nan"),
            "reading": 20.0,
        }
        inf_ts = {
            "device_id": "Device-A",
            "timestamp": float("inf"),
            "reading": 20.0,
        }

        for msg in (nan_reading, inf_reading, neginf_reading, nan_ts, inf_ts):
            with self.assertRaises(ValueError):
                validate_sensor_message(msg)

        result = process_sensor_messages(
            [nan_reading, inf_reading, neginf_reading, nan_ts, inf_ts]
        )
        self.assertEqual(len(result.accepted), 0)
        self.assertEqual(len(result.invalid), 5)

    # 9. Missing fields
    def test_missing_fields(self) -> None:
        """Test that messages missing required fields or non-dict payloads are rejected."""
        # Non-dict
        with self.assertRaises(TypeError):
            validate_sensor_message("not a dict")  # type: ignore[arg-type]
        with self.assertRaises(TypeError):
            validate_sensor_message([1, 2, 3])  # type: ignore[arg-type]

        # Missing keys
        missing_device = {"timestamp": 1, "reading": 20.0}
        missing_ts = {"device_id": "Device-A", "reading": 20.0}
        missing_reading = {"device_id": "Device-A", "timestamp": 1}

        for msg in (missing_device, missing_ts, missing_reading):
            with self.assertRaises(ValueError):
                validate_sensor_message(msg)

        result = process_sensor_messages(
            ["string", missing_device, missing_ts, missing_reading]
        )
        self.assertEqual(len(result.accepted), 0)
        self.assertEqual(len(result.invalid), 4)

    # 10. Invalid device ID
    def test_invalid_device_id(self) -> None:
        """Test that empty or non-string device IDs are rejected."""
        empty_device = {"device_id": "", "timestamp": 1, "reading": 20.0}
        whitespace_device = {"device_id": "   ", "timestamp": 1, "reading": 20.0}
        numeric_device = {"device_id": 12345, "timestamp": 1, "reading": 20.0}
        none_device = {"device_id": None, "timestamp": 1, "reading": 20.0}

        with self.assertRaises(ValueError):
            validate_sensor_message(empty_device)
        with self.assertRaises(ValueError):
            validate_sensor_message(whitespace_device)
        with self.assertRaises(TypeError):
            validate_sensor_message(numeric_device)
        with self.assertRaises(TypeError):
            validate_sensor_message(none_device)

    # 11. Invalid timestamp
    def test_invalid_timestamp(self) -> None:
        """Test that string, boolean, or None timestamps are rejected."""
        str_ts = {
            "device_id": "Device-A",
            "timestamp": "2026-11-18",
            "reading": 20.0,
        }
        bool_ts = {"device_id": "Device-A", "timestamp": True, "reading": 20.0}
        none_ts = {"device_id": "Device-A", "timestamp": None, "reading": 20.0}

        with self.assertRaises(TypeError):
            validate_sensor_message(str_ts)
        with self.assertRaises(TypeError):
            validate_sensor_message(bool_ts)
        with self.assertRaises(TypeError):
            validate_sensor_message(none_ts)

    # 12. Deterministic ordering for equal timestamps
    def test_deterministic_ordering_for_equal_timestamps(self) -> None:
        """Test that messages with identical timestamps sort deterministically across permutations."""
        msg1 = {"device_id": "Device-C", "timestamp": 10, "reading": 30.0}
        msg2 = {"device_id": "Device-A", "timestamp": 10, "reading": 10.0}
        msg3 = {"device_id": "Device-B", "timestamp": 10, "reading": 20.0}

        # Permutation 1
        res1 = process_sensor_messages([msg1, msg2, msg3])
        # Permutation 2
        res2 = process_sensor_messages([msg3, msg1, msg2])

        expected_ids = ["Device-A", "Device-B", "Device-C"]
        self.assertEqual([m["device_id"] for m in res1.accepted], expected_ids)
        self.assertEqual([m["device_id"] for m in res2.accepted], expected_ids)

    # 13. Required fixture test
    def test_required_fixture_behavior(self) -> None:
        """Verify the complete processing of the documented course fixture."""
        fixture = get_required_fixture()
        result = process_sensor_messages(fixture)

        # Accepted messages
        self.assertEqual(len(result.accepted), 3)
        # Device A messages must appear in timestamp order 1 then 2
        device_a_msgs = [
            m for m in result.accepted if m["device_id"] == "Device-A"
        ]
        self.assertEqual(len(device_a_msgs), 2)
        self.assertEqual(device_a_msgs[0]["timestamp"], 1)
        self.assertEqual(device_a_msgs[1]["timestamp"], 2)

        # Zero reading message must be accepted
        device_c = next(
            m for m in result.accepted if m["device_id"] == "Device-C"
        )
        self.assertEqual(device_c["reading"], 0)

        # Duplicate must be reported separately
        self.assertEqual(len(result.duplicates), 1)
        self.assertEqual(result.duplicates[0]["message"]["device_id"], "Device-A")
        self.assertEqual(result.duplicates[0]["message"]["timestamp"], 1)

        # Invalid messages must be reported
        self.assertEqual(len(result.invalid), 3)
        invalid_devices = [inv["message"]["device_id"] for inv in result.invalid]
        self.assertIn("Device-B", invalid_devices)  # string reading "25.5"
        self.assertIn("", invalid_devices)  # empty device id
        self.assertIn("Device-D", invalid_devices)  # NaN timestamp


if __name__ == "__main__":
    unittest.main()
