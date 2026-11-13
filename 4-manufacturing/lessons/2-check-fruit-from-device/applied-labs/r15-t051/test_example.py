import json
import unittest

from example import validate_messages


def msg(device_id, timestamp, reading):
    return json.dumps(
        {"device_id": device_id, "timestamp": timestamp, "reading": reading}
    )


class NormalCases(unittest.TestCase):
    def test_orders_by_timestamp(self):
        accepted, errors = validate_messages([msg("A", 2, 0.9), msg("A", 1, 0.8)])
        self.assertEqual([m["timestamp"] for m in accepted], [1, 2])
        self.assertEqual(errors, [])

    def test_duplicate_device_timestamp_reported(self):
        accepted, errors = validate_messages(
            [msg("A", 2, 0.9), msg("A", 1, 0.8), msg("A", 1, 0.7)]
        )
        self.assertEqual(len(accepted), 2)
        self.assertEqual(errors, [(2, "duplicate device/timestamp: A/1")])

    def test_string_reading_rejected(self):
        accepted, errors = validate_messages([msg("A", 1, "high")])
        self.assertEqual(accepted, [])
        self.assertEqual(errors, [(0, "reading must be numeric")])


class BoundaryCases(unittest.TestCase):
    def test_empty_input(self):
        self.assertEqual(validate_messages([]), ([], []))

    def test_same_timestamp_different_devices_allowed(self):
        accepted, errors = validate_messages([msg("A", 1, 1), msg("B", 1, 1)])
        self.assertEqual(len(accepted), 2)
        self.assertEqual(errors, [])

    def test_zero_and_negative_readings_allowed(self):
        accepted, errors = validate_messages([msg("A", 1, 0), msg("A", 2, -3.5)])
        self.assertEqual(len(accepted), 2)

    def test_boolean_reading_rejected(self):
        accepted, errors = validate_messages([msg("A", 1, True)])
        self.assertEqual(accepted, [])
        self.assertEqual(len(errors), 1)


class FailureCases(unittest.TestCase):
    def test_malformed_json(self):
        accepted, errors = validate_messages(["{not json"])
        self.assertEqual(errors, [(0, "malformed JSON")])

    def test_missing_field(self):
        accepted, errors = validate_messages(['{"device_id": "A", "timestamp": 1}'])
        self.assertEqual(errors, [(0, "missing field: reading")])

    def test_non_object_message(self):
        accepted, errors = validate_messages(["[1, 2, 3]"])
        self.assertEqual(errors, [(0, "message must be a JSON object")])


if __name__ == "__main__":
    unittest.main()
