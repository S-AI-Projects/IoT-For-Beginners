"""Unit tests for Sensor-Message Validation — Invariant and State Trace (Task R15-T024).

Verifies payload validation, duplicate detection, chronological sorting,
intermediate state trace accuracy, and pipeline invariant verification
using Python's standard library unittest framework.
"""

from copy import deepcopy
import os
import sys
import unittest

# Ensure the module directory is accessible for direct execution or discovery
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from example import (  # noqa: E402
    ProcessingOutcome,
    check_pipeline_invariant,
    get_required_fixture,
    parse_and_validate_message,
    process_message_stream,
)


class TestSensorMessageValidationTrace(unittest.TestCase):
    """Test suite for telemetry validation, state tracing, and invariant checks."""

    # 1. Required normal fixture behavior
    def test_required_fixture_behavior(self) -> None:
        """Verify the exact required 4-message fixture outcomes and ordering."""
        fixture = get_required_fixture()
        result = process_message_stream(fixture)

        # Invariant must hold
        self.assertTrue(check_pipeline_invariant(fixture, result))

        # Accepted messages: 2 total, ordered A/1 followed by A/2
        self.assertEqual(len(result.accepted), 2)
        self.assertEqual(result.accepted[0]["device_id"], "Device-A")
        self.assertEqual(result.accepted[0]["timestamp"], 1)
        self.assertEqual(result.accepted[0]["reading"], 10)

        self.assertEqual(result.accepted[1]["device_id"], "Device-A")
        self.assertEqual(result.accepted[1]["timestamp"], 2)
        self.assertEqual(result.accepted[1]["reading"], 20)

        # Duplicate: 1 total (timestamp 1, reading 11)
        self.assertEqual(len(result.duplicates), 1)
        self.assertEqual(result.duplicates[0]["message"]["timestamp"], 1)
        self.assertEqual(result.duplicates[0]["message"]["reading"], 11)

        # Rejected: 1 total (timestamp 3, string reading)
        self.assertEqual(len(result.rejected), 1)
        self.assertEqual(
            result.rejected[0]["input"]["reading"], "not-a-number"
        )
        self.assertIn("reading", result.rejected[0]["reason"].lower())

    # 2. Timestamp ordering when input arrives out of order
    def test_timestamp_ordering_out_of_order(self) -> None:
        """Verify that accepted messages are sorted ascending by timestamp."""
        unordered = [
            {"device_id": "Device-B", "timestamp": 50, "reading": 5.0},
            {"device_id": "Device-B", "timestamp": 10, "reading": 1.0},
            {"device_id": "Device-B", "timestamp": 30, "reading": 3.0},
        ]
        result = process_message_stream(unordered)
        self.assertTrue(check_pipeline_invariant(unordered, result))
        self.assertEqual([m["timestamp"] for m in result.accepted], [10, 30, 50])

    # 3. Duplicate detection
    def test_duplicate_detection(self) -> None:
        """Verify that duplicate (device_id, timestamp) pairs are isolated."""
        inputs = [
            {"device_id": "Sensor-1", "timestamp": 100, "reading": 42.0},
            {"device_id": "Sensor-1", "timestamp": 100, "reading": 99.9},  # duplicate
            {"device_id": "Sensor-1", "timestamp": 100, "reading": 0.0},   # duplicate
        ]
        result = process_message_stream(inputs)
        self.assertTrue(check_pipeline_invariant(inputs, result))
        self.assertEqual(len(result.accepted), 1)
        self.assertEqual(result.accepted[0]["reading"], 42.0)
        self.assertEqual(len(result.duplicates), 2)
        self.assertEqual(len(result.rejected), 0)

    # 4. Invalid message does not reserve identity
    def test_invalid_message_does_not_reserve_identity(self) -> None:
        """Verify that a rejected message does not prevent a subsequent valid message with the same key."""
        inputs = [
            {"device_id": "Device-X", "timestamp": 5, "reading": "bad-string"},  # REJECTED
            {"device_id": "Device-X", "timestamp": 5, "reading": 50.0},          # ACCEPTED!
        ]
        result = process_message_stream(inputs)
        self.assertTrue(check_pipeline_invariant(inputs, result))
        self.assertEqual(len(result.rejected), 1)
        self.assertEqual(len(result.accepted), 1)
        self.assertEqual(result.accepted[0]["reading"], 50.0)
        self.assertEqual(len(result.duplicates), 0)

    # 5. String reading rejection
    def test_string_reading_rejection(self) -> None:
        """Verify that string readings are rejected."""
        inputs = [
            {"device_id": "Device-A", "timestamp": 1, "reading": "not-a-number"},
            {"device_id": "Device-A", "timestamp": 2, "reading": "25.5"},
        ]
        result = process_message_stream(inputs)
        self.assertEqual(len(result.accepted), 0)
        self.assertEqual(len(result.rejected), 2)
        self.assertIn("reading", result.rejected[0]["reason"].lower())
        self.assertIn("reading", result.rejected[1]["reason"].lower())

    # 6. Missing fields
    def test_missing_fields(self) -> None:
        """Verify that messages missing any required field are rejected."""
        missing_device = {"timestamp": 1, "reading": 10}
        missing_ts = {"device_id": "Device-A", "reading": 10}
        missing_reading = {"device_id": "Device-A", "timestamp": 1}

        result = process_message_stream([missing_device, missing_ts, missing_reading])
        self.assertEqual(len(result.accepted), 0)
        self.assertEqual(len(result.rejected), 3)

    # 7. Empty device ID
    def test_empty_device_id(self) -> None:
        """Verify that empty, whitespace-only, or non-string device IDs are rejected."""
        empty_id = {"device_id": "", "timestamp": 1, "reading": 10}
        whitespace_id = {"device_id": "   ", "timestamp": 1, "reading": 10}
        numeric_id = {"device_id": 999, "timestamp": 1, "reading": 10}

        result = process_message_stream([empty_id, whitespace_id, numeric_id])
        self.assertEqual(len(result.accepted), 0)
        self.assertEqual(len(result.rejected), 3)

    # 8. Invalid timestamp
    def test_invalid_timestamp(self) -> None:
        """Verify that string, boolean, or None timestamps are rejected."""
        str_ts = {"device_id": "Device-A", "timestamp": "2026-11-18", "reading": 10}
        bool_ts = {"device_id": "Device-A", "timestamp": True, "reading": 10}
        none_ts = {"device_id": "Device-A", "timestamp": None, "reading": 10}

        result = process_message_stream([str_ts, bool_ts, none_ts])
        self.assertEqual(len(result.accepted), 0)
        self.assertEqual(len(result.rejected), 3)

    # 9. Boolean and non-finite numeric values
    def test_boolean_and_non_finite_numeric_values(self) -> None:
        """Verify that booleans and non-finite floats (NaN, Inf) are rejected."""
        bool_reading_true = {"device_id": "Device-A", "timestamp": 1, "reading": True}
        bool_reading_false = {"device_id": "Device-A", "timestamp": 2, "reading": False}
        nan_reading = {"device_id": "Device-A", "timestamp": 3, "reading": float("nan")}
        inf_reading = {"device_id": "Device-A", "timestamp": 4, "reading": float("inf")}
        nan_ts = {"device_id": "Device-A", "timestamp": float("nan"), "reading": 10}
        inf_ts = {"device_id": "Device-A", "timestamp": float("-inf"), "reading": 10}

        inputs = [
            bool_reading_true,
            bool_reading_false,
            nan_reading,
            inf_reading,
            nan_ts,
            inf_ts,
        ]
        result = process_message_stream(inputs)
        self.assertEqual(len(result.accepted), 0)
        self.assertEqual(len(result.rejected), 6)

    # 10. Malformed JSON
    def test_malformed_json(self) -> None:
        """Verify that malformed JSON strings or non-dict payloads are rejected."""
        bad_json_string = '{"device_id": "Device-A", "timestamp": 1, "reading": '  # truncated
        json_array_payload = '[{"device_id": "Device-A", "timestamp": 1, "reading": 10}]'
        raw_number_payload = 12345

        result = process_message_stream(
            [bad_json_string, json_array_payload, raw_number_payload]
        )
        self.assertEqual(len(result.accepted), 0)
        self.assertEqual(len(result.rejected), 3)

        # Well-formed JSON string should succeed
        valid_json_string = '{"device_id": "Device-A", "timestamp": 1, "reading": 10}'
        res_valid = process_message_stream([valid_json_string])
        self.assertEqual(len(res_valid.accepted), 1)

    # 11. State trace correctness
    def test_state_trace_correctness(self) -> None:
        """Verify that the intermediate state trace records accurate step-by-step state."""
        fixture = get_required_fixture()
        result = process_message_stream(fixture)

        self.assertEqual(len(result.trace), len(fixture))

        # Step 1: Input A/2 -> Accepted (1), Dup (0), Rej (0)
        self.assertEqual(result.trace[0].step_number, 1)
        self.assertEqual(result.trace[0].outcome.status, "ACCEPTED")
        self.assertEqual(len(result.trace[0].accepted_so_far), 1)
        self.assertEqual(len(result.trace[0].duplicates_so_far), 0)
        self.assertEqual(len(result.trace[0].rejected_so_far), 0)

        # Step 2: Input A/1 -> Accepted (2: ordered A/1, A/2), Dup (0), Rej (0)
        self.assertEqual(result.trace[1].step_number, 2)
        self.assertEqual(result.trace[1].outcome.status, "ACCEPTED")
        self.assertEqual(len(result.trace[1].accepted_so_far), 2)
        self.assertEqual(result.trace[1].accepted_so_far[0]["timestamp"], 1)
        self.assertEqual(result.trace[1].accepted_so_far[1]["timestamp"], 2)

        # Step 3: Input A/1 (dup) -> Accepted (2), Dup (1), Rej (0)
        self.assertEqual(result.trace[2].step_number, 3)
        self.assertEqual(result.trace[2].outcome.status, "DUPLICATE")
        self.assertEqual(len(result.trace[2].accepted_so_far), 2)
        self.assertEqual(len(result.trace[2].duplicates_so_far), 1)

        # Step 4: Input A/3 ("not-a-number") -> Accepted (2), Dup (1), Rej (1)
        self.assertEqual(result.trace[3].step_number, 4)
        self.assertEqual(result.trace[3].outcome.status, "REJECTED")
        self.assertEqual(len(result.trace[3].accepted_so_far), 2)
        self.assertEqual(len(result.trace[3].duplicates_so_far), 1)
        self.assertEqual(len(result.trace[3].rejected_so_far), 1)

    # 12. Invariant correctness
    def test_invariant_correctness(self) -> None:
        """Verify that check_pipeline_invariant passes on valid empty and non-empty streams."""
        # Empty stream
        empty_res = process_message_stream([])
        self.assertTrue(check_pipeline_invariant([], empty_res))

        # Single valid message
        single = [{"device_id": "Device-1", "timestamp": 1, "reading": 0}]
        single_res = process_message_stream(single)
        self.assertTrue(check_pipeline_invariant(single, single_res))

    # 13. Deliberately corrupted output being detected
    def test_deliberate_corruption_detection(self) -> None:
        """Verify that corrupted outputs violate invariants and raise AssertionError."""
        fixture = get_required_fixture()
        clean_result = process_message_stream(fixture)

        # 13.1 Corrupt timestamp order: swap accepted items
        corrupt_order = deepcopy(clean_result)
        corrupt_order.accepted.reverse()
        corrupt_order.trace[-1].accepted_so_far.reverse()
        with self.assertRaises(AssertionError) as ctx:
            check_pipeline_invariant(fixture, corrupt_order)
        self.assertIn("sorting rule", str(ctx.exception).lower())

        # 13.2 Inject duplicate into accepted
        corrupt_dup = deepcopy(clean_result)
        corrupt_dup.accepted.append(corrupt_dup.accepted[0])
        corrupt_dup.trace[-1].accepted_so_far.append(corrupt_dup.accepted[0])
        with self.assertRaises(AssertionError) as ctx:
            check_pipeline_invariant(fixture, corrupt_dup)
        self.assertTrue(
            any(
                term in str(ctx.exception).lower()
                for term in ("duplicate", "total", "snapshot", "counts")
            )
        )

        # 13.3 Desynchronize trace state and final output
        corrupt_desync = deepcopy(clean_result)
        corrupt_desync.accepted.pop()
        with self.assertRaises(AssertionError) as ctx:
            check_pipeline_invariant(fixture, corrupt_desync)
        self.assertIn("agree with the last trace state", str(ctx.exception))

    # 14. Corrupted intermediate trace snapshots
    def test_corrupted_intermediate_trace_snapshots(self) -> None:
        """Verify that tampering with intermediate trace snapshots raises AssertionError."""
        fixture = get_required_fixture()
        clean_result = process_message_stream(fixture)

        # 14.1 Corrupt count in intermediate snapshot
        corrupt_counts = deepcopy(clean_result)
        corrupt_counts.trace[1].accepted_so_far.pop()
        with self.assertRaises(AssertionError) as ctx:
            check_pipeline_invariant(fixture, corrupt_counts)
        self.assertTrue(
            "snapshot total" in str(ctx.exception).lower()
            or "inconsistent with intermediate snapshot counts" in str(ctx.exception).lower()
        )

        # 14.2 Corrupt sorting within an intermediate snapshot
        corrupt_intermediate_sort = deepcopy(clean_result)
        corrupt_intermediate_sort.trace[1].accepted_so_far.reverse()
        with self.assertRaises(AssertionError) as ctx:
            check_pipeline_invariant(fixture, corrupt_intermediate_sort)
        self.assertIn("violates sorting rule", str(ctx.exception).lower())

    # 15. Incorrect step numbers
    def test_incorrect_step_numbers(self) -> None:
        """Verify that non-sequential or non-1-based step numbers raise AssertionError."""
        fixture = get_required_fixture()
        clean_result = process_message_stream(fixture)

        # 15.1 Step number starts at 0 instead of 1
        corrupt_zero_start = deepcopy(clean_result)
        corrupt_zero_start.trace[0].step_number = 0
        with self.assertRaises(AssertionError) as ctx:
            check_pipeline_invariant(fixture, corrupt_zero_start)
        self.assertIn("step_number", str(ctx.exception).lower())

        # 15.2 Non-sequential step number
        corrupt_seq = deepcopy(clean_result)
        corrupt_seq.trace[2].step_number = 99
        with self.assertRaises(AssertionError) as ctx:
            check_pipeline_invariant(fixture, corrupt_seq)
        self.assertIn("step_number", str(ctx.exception).lower())

    # 16. Tie-breaking order and corruption detection
    def test_incorrect_tie_breaking_order(self) -> None:
        """Verify that tie-breaking (timestamp, device_id, reading) is enforced and detected."""
        # Two devices publishing at identical timestamps
        inputs = [
            {"device_id": "Device-B", "timestamp": 100, "reading": 20.0},
            {"device_id": "Device-A", "timestamp": 100, "reading": 10.0},
        ]
        result = process_message_stream(inputs)
        self.assertTrue(check_pipeline_invariant(inputs, result))

        # Device-A must precede Device-B because timestamps are equal
        self.assertEqual(result.accepted[0]["device_id"], "Device-A")
        self.assertEqual(result.accepted[1]["device_id"], "Device-B")

        # Deliberately invert the tie-break ordering
        corrupt_tie = deepcopy(result)
        corrupt_tie.accepted.reverse()
        corrupt_tie.trace[-1].accepted_so_far.reverse()
        with self.assertRaises(AssertionError) as ctx:
            check_pipeline_invariant(inputs, corrupt_tie)
        self.assertIn("sorting rule", str(ctx.exception).lower())

    # 17. Tampering with intermediate snapshot content without changing length
    def test_corrupted_intermediate_snapshot_content_without_length_change(self) -> None:
        """Verify that modifying snapshot message content without changing list length raises AssertionError."""
        fixture = get_required_fixture()
        clean_result = process_message_stream(fixture)

        # 17.1 Tamper with an accepted message in intermediate snapshot (step 2)
        # Change reading from 10 to 15 (valid number, preserves sorting and list length)
        corrupt_accepted_content = deepcopy(clean_result)
        corrupt_accepted_content.trace[1].accepted_so_far[0]["reading"] = 15
        with self.assertRaises(AssertionError) as ctx:
            check_pipeline_invariant(fixture, corrupt_accepted_content)
        self.assertIn("accepted_so_far", str(ctx.exception).lower())

        # 17.2 Tamper with a duplicate message in intermediate snapshot (step 3)
        # Modify duplicate message reading without changing list length
        corrupt_dup_content = deepcopy(clean_result)
        corrupt_dup_content.trace[2].duplicates_so_far[0]["message"]["reading"] = 999
        with self.assertRaises(AssertionError) as ctx:
            check_pipeline_invariant(fixture, corrupt_dup_content)
        self.assertIn("duplicates_so_far", str(ctx.exception).lower())

        # 17.3 Tamper with raw_input at an intermediate step
        corrupt_raw_input = deepcopy(clean_result)
        corrupt_raw_input.trace[0].raw_input = {
            "device_id": "Device-TAMPERED",
            "timestamp": 2,
            "reading": 20,
        }
        with self.assertRaises(AssertionError) as ctx:
            check_pipeline_invariant(fixture, corrupt_raw_input)
        self.assertIn("raw_input", str(ctx.exception).lower())

        # 17.4 Tamper with step outcome status
        corrupt_outcome = deepcopy(clean_result)
        corrupt_outcome.trace[0].outcome = ProcessingOutcome(
            status="REJECTED", reason="Tampered"
        )
        with self.assertRaises(AssertionError) as ctx:
            check_pipeline_invariant(fixture, corrupt_outcome)
        self.assertIn("outcome status", str(ctx.exception).lower())


if __name__ == "__main__":
    unittest.main()
