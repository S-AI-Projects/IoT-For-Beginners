import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from example import FIXTURE, MessageError, SensorStream, parse_message, process  # noqa: E402


def msg(device="A", ts=1, reading=1.0):
    return '{"device_id": "%s", "timestamp": %s, "reading": %s}' % (device, ts, reading)


class Ordering(unittest.TestCase):
    def test_a2_then_a1_returned_in_order_1_2(self):
        accepted, errors = process([msg("A", 2), msg("A", 1)])
        self.assertEqual([m[1] for m in accepted], [1, 2])
        self.assertEqual(errors, [])

    def test_ties_ordered_by_device_id(self):
        accepted, _ = process([msg("B", 5), msg("A", 5)])
        self.assertEqual([m[0] for m in accepted], ["A", "B"])

    def test_same_timestamp_different_device_is_not_a_duplicate(self):
        accepted, errors = process([msg("A", 1), msg("B", 1)])
        self.assertEqual(len(accepted), 2)
        self.assertEqual(errors, [])


class Rejections(unittest.TestCase):
    def test_duplicate_reported(self):
        accepted, errors = process([msg("A", 1), msg("A", 1)])
        self.assertEqual(len(accepted), 1)
        self.assertEqual(errors[0][0], 1)
        self.assertIn("duplicate", errors[0][1])

    def test_string_reading_rejected(self):
        with self.assertRaises(MessageError) as cm:
            parse_message('{"device_id": "A", "timestamp": 1, "reading": "21.5"}')
        self.assertIn("reading must be a number", str(cm.exception))

    def test_missing_fields(self):
        for field in ("device_id", "timestamp", "reading"):
            data = {"device_id": "A", "timestamp": 1, "reading": 1}
            del data[field]
            import json
            with self.assertRaises(MessageError) as cm:
                parse_message(json.dumps(data))
            self.assertIn("missing field: " + field, str(cm.exception))

    def test_malformed_and_wrong_types(self):
        bad = ["{bad", "", "[]", "5", "null",
               '{"device_id": "", "timestamp": 1, "reading": 1}',
               '{"device_id": "A", "timestamp": -1, "reading": 1}',
               '{"device_id": "A", "timestamp": 1.5, "reading": 1}',
               '{"device_id": "A", "timestamp": true, "reading": 1}',
               '{"device_id": "A", "timestamp": 1, "reading": true}',
               '{"device_id": "A", "timestamp": 1, "reading": NaN}']
        for raw in bad:
            with self.subTest(raw=raw):
                with self.assertRaises(MessageError):
                    parse_message(raw)

    def test_non_string_input(self):
        with self.assertRaises(MessageError):
            parse_message(None)


class Recovery(unittest.TestCase):
    def test_error_does_not_change_state(self):
        s = SensorStream()
        s.ingest(msg("A", 1))
        with self.assertRaises(MessageError):
            s.ingest('{"device_id": "A", "timestamp": 2, "reading": "x"}')
        self.assertEqual(len(s.ordered()), 1)

    def test_next_valid_input_after_failure_is_accepted(self):
        s = SensorStream()
        with self.assertRaises(MessageError) as cm:
            s.ingest('{"device_id": "A", "timestamp": 3, "reading": 22.0')
        self.assertIn("malformed JSON", str(cm.exception))
        self.assertEqual(s.ingest(msg("A", 3, 22.0)), ("A", 3, 22.0))

    def test_documented_fixture(self):
        accepted, errors = process(FIXTURE)
        self.assertEqual(accepted, [("A", 1, 20.0), ("A", 2, 21.5), ("A", 3, 22.0)])
        self.assertEqual([i for i, _ in errors], [2, 3, 4, 5])
        self.assertIn("duplicate", errors[0][1])
        self.assertIn("reading must be a number, got str", errors[1][1])
        self.assertEqual(errors[2][1], "missing field: reading")
        self.assertIn("malformed JSON", errors[3][1])


if __name__ == "__main__":
    unittest.main()
