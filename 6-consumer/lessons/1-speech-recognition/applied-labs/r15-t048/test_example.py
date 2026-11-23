import os
import unittest
from example import FIXTURE, brief, process, validate


class MessageContractTests(unittest.TestCase):
    def test_required_fixture(self):
        self.assertEqual(brief(process(FIXTURE)),
                         "accepted=[A@1,A@2] rejected=[2:duplicate_device_timestamp,3:invalid_reading]")

    def test_sorted_records_and_duplicate_identity(self):
        result = process(FIXTURE)
        self.assertEqual([r["timestamp"] for r in result["accepted"]], [1, 2])
        self.assertEqual(result["accepted"][0]["reading"], 8)
        self.assertEqual(result["rejected"][0]["reason"], "duplicate_device_timestamp")

    def test_different_devices_same_timestamp_allowed(self):
        raws = ['{"device_id":"A","timestamp":1,"reading":1}',
                '{"device_id":"B","timestamp":1,"reading":2}']
        self.assertEqual(len(process(raws)["accepted"]), 2)

    def test_bad_json_and_reading(self):
        for raw in ('{', '[]', '{"device_id":"A","timestamp":1,"reading":"5"}',
                    '{"device_id":"A","timestamp":1,"reading":true}',
                    '{"device_id":"","timestamp":1,"reading":1}',
                    '{"device_id":"A","timestamp":true,"reading":1}'):
            with self.subTest(raw=raw), self.assertRaises(ValueError):
                validate(raw)

    def test_empty_input(self):
        self.assertEqual(process([]), {"accepted": [], "rejected": []})

    @unittest.skipUnless(os.getenv("RUN_INTENTIONAL_FAILURE") == "1", "negative test runs separately")
    def test_deliberately_wrong_result_fails(self):
        self.assertEqual(len(process(FIXTURE)["accepted"]), 3)

    def test_three_controlled_sizes(self):
        from example import evaluate, make_fixture
        rows = evaluate()
        self.assertEqual([r["inputs"] for r in rows], [4, 8, 16])
        self.assertEqual([(r["accepted"], r["rejected"]) for r in rows],
                         [(2, 2), (4, 4), (8, 8)])
        self.assertTrue(all(r["count_correct"] for r in rows))
        self.assertTrue(all(r["acceptance_fraction"] == .5 for r in rows))
        self.assertEqual(len(make_fixture(4)), 16)

    def test_bad_fixture_size(self):
        from example import make_fixture
        for size in (0, -1, 1.5, True):
            with self.subTest(size=size), self.assertRaises(ValueError):
                make_fixture(size)

if __name__ == "__main__":
    unittest.main()
