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

    def test_local_callable_adapter(self):
        from example import local_source, run_with_source
        self.assertEqual(run_with_source(local_source), process(FIXTURE))
        self.assertEqual(run_with_source(lambda: []), process([]))

    def test_adapter_can_swap_fixtures(self):
        from example import run_with_source
        result = run_with_source(lambda: [FIXTURE[0]])
        self.assertEqual(len(result["accepted"]), 1)

    def test_adapter_requires_callable(self):
        from example import run_with_source
        with self.assertRaises(TypeError):
            run_with_source(FIXTURE)

if __name__ == "__main__":
    unittest.main()
