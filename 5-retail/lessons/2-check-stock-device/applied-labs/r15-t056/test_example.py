import unittest
from example import validate_and_order_messages


class TestSensorMessageValidation(unittest.TestCase):
    def test_exact_worked_example(self):
        inputs = [
            '{"device_id": "A", "timestamp": 2, "reading": 15}',
            '{"device_id": "A", "timestamp": 1, "reading": 12}',
            '{"device_id": "A", "timestamp": 1, "reading": 99}',
            '{"device_id": "A", "timestamp": 3, "reading": "ten"}',
        ]
        result = validate_and_order_messages(inputs)

        self.assertEqual(
            result["accepted"],
            [
                {"device_id": "A", "timestamp": 1, "reading": 12},
                {"device_id": "A", "timestamp": 2, "reading": 15},
            ],
        )
        self.assertEqual(len(result["rejected"]), 2)
        self.assertIn("Duplicate device/timestamp pair: A/1", result["rejected"][0]["reason"])
        self.assertIn("Reading must be numeric", result["rejected"][1]["reason"])

    def test_boundary_and_malformed_cases(self):
        inputs = [
            '{"device_id": "B", "timestamp": 0, "reading": 0.0}',
            '{"device_id": "A", "timestamp": 1, "reading": 5}',
            'not-valid-json',
            '{"device_id": "", "timestamp": 5, "reading": 10}',
            '{"device_id": "B", "timestamp": true, "reading": 10}',
            '{"device_id": "B", "timestamp": 5, "reading": false}',
        ]
        result = validate_and_order_messages(inputs)
        self.assertEqual(len(result["accepted"]), 2)
        self.assertEqual(result["accepted"][0]["device_id"], "B")
        self.assertEqual(result["accepted"][1]["device_id"], "A")
        self.assertEqual(len(result["rejected"]), 4)


if __name__ == "__main__":
    unittest.main()
