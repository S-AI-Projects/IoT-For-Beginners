"""Unit tests for Sensor-Message Validation — Offline Service Adapter (Task R15-T025).

Verifies payload validation, deduplication, deterministic chronological sorting,
callable service adapter injection, delivery classification, and contract guarantees
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
    InMemoryServiceAdapter,
    ProcessingResult,
    ServiceAcknowledgement,
    get_required_fixture,
    parse_and_validate_message,
    process_message_stream,
    verify_pipeline_contract,
)


class TestOfflineServiceAdapter(unittest.TestCase):
    """Test suite for sensor telemetry processing and offline service adapter contract."""

    # 1. Required fixture behavior
    def test_required_fixture_behavior(self) -> None:
        """Verify the exact required 4-message fixture outcomes, delivery, and ordering."""
        fixture = get_required_fixture()
        adapter = InMemoryServiceAdapter()
        result = process_message_stream(fixture, service_adapter=adapter)

        # Invariant and delivery contract must hold
        self.assertTrue(verify_pipeline_contract(fixture, result, adapter=adapter))

        # Accepted messages: 2 total, timestamps [1, 2]
        self.assertEqual(len(result.accepted), 2)
        self.assertEqual([m["timestamp"] for m in result.accepted], [1, 2])
        self.assertEqual(result.accepted[0]["device_id"], "Device-A")
        self.assertEqual(result.accepted[0]["reading"], 10)
        self.assertEqual(result.accepted[1]["device_id"], "Device-A")
        self.assertEqual(result.accepted[1]["reading"], 20)

        # Duplicate: 1 total (Device-A, timestamp 1, reading 10 again)
        self.assertEqual(len(result.duplicates), 1)
        self.assertEqual(result.duplicates[0]["message"]["timestamp"], 1)

        # Rejected: 1 total (Device-A, timestamp 3, string reading 'hot')
        self.assertEqual(len(result.rejected), 1)
        self.assertEqual(result.rejected[0]["input"]["reading"], "hot")
        self.assertIn("reading", result.rejected[0]["reason"].lower())

        # Delivery: 2 confirmed delivered, 0 failed
        self.assertEqual(len(result.delivered), 2)
        self.assertEqual(len(result.failed_deliveries), 0)
        self.assertEqual(len(result.acknowledgements), 2)
        self.assertTrue(all(ack.status == "DELIVERED" for ack in result.acknowledgements))

    # 2. Chronological ordering
    def test_chronological_ordering(self) -> None:
        """Verify that accepted messages are sorted ascending by timestamp."""
        unordered = [
            {"device_id": "Device-B", "timestamp": 50, "reading": 5.0},
            {"device_id": "Device-B", "timestamp": 10, "reading": 1.0},
            {"device_id": "Device-B", "timestamp": 30, "reading": 3.0},
        ]
        result = process_message_stream(unordered)
        self.assertTrue(verify_pipeline_contract(unordered, result))
        self.assertEqual([m["timestamp"] for m in result.accepted], [10, 30, 50])

    # 3. Chronological ordering tie-breaking across devices
    def test_chronological_ordering_tie_breaking(self) -> None:
        """Verify tie-breaking (timestamp, device_id, reading) for matching timestamps."""
        inputs = [
            {"device_id": "Device-B", "timestamp": 100, "reading": 20.0},
            {"device_id": "Device-A", "timestamp": 100, "reading": 10.0},
        ]
        result = process_message_stream(inputs)
        self.assertTrue(verify_pipeline_contract(inputs, result))
        self.assertEqual(result.accepted[0]["device_id"], "Device-A")
        self.assertEqual(result.accepted[1]["device_id"], "Device-B")

    # 4. Duplicate detection
    def test_duplicate_detection(self) -> None:
        """Verify that duplicate (device_id, timestamp) pairs are isolated."""
        inputs = [
            {"device_id": "Sensor-1", "timestamp": 100, "reading": 42.0},
            {"device_id": "Sensor-1", "timestamp": 100, "reading": 99.9},  # duplicate
            {"device_id": "Sensor-1", "timestamp": 100, "reading": 0.0},   # duplicate
        ]
        result = process_message_stream(inputs)
        self.assertTrue(verify_pipeline_contract(inputs, result))
        self.assertEqual(len(result.accepted), 1)
        self.assertEqual(result.accepted[0]["reading"], 42.0)
        self.assertEqual(len(result.duplicates), 2)
        self.assertEqual(len(result.rejected), 0)

    # 5. Invalid string reading rejection
    def test_invalid_string_reading(self) -> None:
        """Verify that string readings (e.g. 'hot' or numeric strings) are rejected."""
        inputs = [
            {"device_id": "Device-A", "timestamp": 1, "reading": "hot"},
            {"device_id": "Device-A", "timestamp": 2, "reading": "25.5"},
        ]
        result = process_message_stream(inputs)
        self.assertEqual(len(result.accepted), 0)
        self.assertEqual(len(result.rejected), 2)
        self.assertIn("reading", result.rejected[0]["reason"].lower())
        self.assertIn("reading", result.rejected[1]["reason"].lower())

    # 6. Missing required fields
    def test_missing_fields(self) -> None:
        """Verify that messages missing any required field are rejected."""
        missing_device = {"timestamp": 1, "reading": 10}
        missing_ts = {"device_id": "Device-A", "reading": 10}
        missing_reading = {"device_id": "Device-A", "timestamp": 1}

        result = process_message_stream([missing_device, missing_ts, missing_reading])
        self.assertEqual(len(result.accepted), 0)
        self.assertEqual(len(result.rejected), 3)

    # 7. Empty or invalid device ID
    def test_empty_device_id(self) -> None:
        """Verify that empty, whitespace-only, or non-string device IDs are rejected."""
        empty_id = {"device_id": "", "timestamp": 1, "reading": 10}
        whitespace_id = {"device_id": "   ", "timestamp": 1, "reading": 10}
        numeric_id = {"device_id": 999, "timestamp": 1, "reading": 10}

        result = process_message_stream([empty_id, whitespace_id, numeric_id])
        self.assertEqual(len(result.accepted), 0)
        self.assertEqual(len(result.rejected), 3)

    # 8. Malformed JSON string
    def test_malformed_json(self) -> None:
        """Verify that malformed JSON strings are rejected with ValueError."""
        bad_json = '{"device_id": "Device-A", "timestamp": 1, "reading": '  # truncated
        result = process_message_stream([bad_json])
        self.assertEqual(len(result.accepted), 0)
        self.assertEqual(len(result.rejected), 1)
        self.assertIn("malformed json", result.rejected[0]["reason"].lower())

    # 9. Non-object JSON
    def test_non_object_json(self) -> None:
        """Verify that non-object JSON values (arrays, primitives, numbers) are rejected."""
        json_array = '[{"device_id": "Device-A", "timestamp": 1, "reading": 10}]'
        raw_number = 12345
        raw_bool = True
        raw_str = '"just-a-string"'

        result = process_message_stream([json_array, raw_number, raw_bool, raw_str])
        self.assertEqual(len(result.accepted), 0)
        self.assertEqual(len(result.rejected), 4)

    # 10. Boolean numeric values rejected
    def test_boolean_numeric_values(self) -> None:
        """Verify that booleans used in timestamp or reading fields are rejected."""
        bool_reading_true = {"device_id": "Device-A", "timestamp": 1, "reading": True}
        bool_reading_false = {"device_id": "Device-A", "timestamp": 2, "reading": False}
        bool_ts_true = {"device_id": "Device-A", "timestamp": True, "reading": 10}
        bool_ts_false = {"device_id": "Device-A", "timestamp": False, "reading": 10}

        result = process_message_stream([
            bool_reading_true,
            bool_reading_false,
            bool_ts_true,
            bool_ts_false,
        ])
        self.assertEqual(len(result.accepted), 0)
        self.assertEqual(len(result.rejected), 4)

    # 11. Non-finite numbers rejected
    def test_non_finite_numbers(self) -> None:
        """Verify that NaN and Infinity are rejected."""
        nan_reading = {"device_id": "Device-A", "timestamp": 1, "reading": float("nan")}
        inf_reading = {"device_id": "Device-A", "timestamp": 2, "reading": float("inf")}
        nan_ts = {"device_id": "Device-A", "timestamp": float("nan"), "reading": 10}
        neg_inf_ts = {"device_id": "Device-A", "timestamp": float("-inf"), "reading": 10}

        result = process_message_stream([nan_reading, inf_reading, nan_ts, neg_inf_ts])
        self.assertEqual(len(result.accepted), 0)
        self.assertEqual(len(result.rejected), 4)

    # 12. Valid zero values accepted
    def test_valid_zero_values(self) -> None:
        """Verify that zero is accepted as a valid timestamp and reading."""
        zero_msg = {"device_id": "Device-Zero", "timestamp": 0, "reading": 0.0}
        result = process_message_stream([zero_msg])
        self.assertEqual(len(result.accepted), 1)
        self.assertEqual(result.accepted[0]["timestamp"], 0)
        self.assertEqual(result.accepted[0]["reading"], 0.0)
        self.assertEqual(len(result.delivered), 1)

    # 13. Invalid messages do not reserve identity
    def test_invalid_messages_not_reserving_identity(self) -> None:
        """Verify that a rejected message does not reserve its (device_id, timestamp) key."""
        inputs = [
            {"device_id": "Device-X", "timestamp": 5, "reading": "bad-string"},  # REJECTED
            {"device_id": "Device-X", "timestamp": 5, "reading": 50.0},          # ACCEPTED!
        ]
        result = process_message_stream(inputs)
        self.assertTrue(verify_pipeline_contract(inputs, result))
        self.assertEqual(len(result.rejected), 1)
        self.assertEqual(len(result.accepted), 1)
        self.assertEqual(result.accepted[0]["reading"], 50.0)
        self.assertEqual(len(result.duplicates), 0)

    # 14. Injected callable actually being called
    def test_injected_callable_called(self) -> None:
        """Verify that the injected service adapter callable is invoked for accepted messages only."""
        called_messages = []

        def spy_adapter(msg):
            called_messages.append(msg)
            return ServiceAcknowledgement(
                message_id="spy-ack",
                device_id=msg["device_id"],
                timestamp=msg["timestamp"],
                status="DELIVERED",
                details="Spy adapter acknowledged.",
            )

        fixture = get_required_fixture()
        result = process_message_stream(fixture, service_adapter=spy_adapter)

        # Spy should be called exactly twice (for the 2 accepted messages)
        self.assertEqual(len(called_messages), 2)
        self.assertEqual(len(result.accepted), 2)
        self.assertEqual([m["timestamp"] for m in called_messages], [1, 2])

    # 15. Correct order of messages submitted to the adapter
    def test_correct_order_of_messages_submitted_to_adapter(self) -> None:
        """Verify that messages are passed to the adapter in strictly ascending chronological order."""
        submitted_timestamps = []

        def recording_adapter(msg):
            submitted_timestamps.append(msg["timestamp"])
            return ServiceAcknowledgement(
                message_id="order-ack",
                device_id=msg["device_id"],
                timestamp=msg["timestamp"],
                status="DELIVERED",
                details="Recorded.",
            )

        unordered_inputs = [
            {"device_id": "Dev", "timestamp": 300, "reading": 30},
            {"device_id": "Dev", "timestamp": 100, "reading": 10},
            {"device_id": "Dev", "timestamp": 200, "reading": 20},
        ]
        process_message_stream(unordered_inputs, service_adapter=recording_adapter)
        self.assertEqual(submitted_timestamps, [100, 200, 300])

    # 16. Deterministic adapter acknowledgements
    def test_deterministic_adapter_acknowledgements(self) -> None:
        """Verify that InMemoryServiceAdapter returns consistent, predictable acknowledgements."""
        adapter = InMemoryServiceAdapter()
        inputs = [{"device_id": "Sensor-A", "timestamp": 1234, "reading": 42}]
        result = process_message_stream(inputs, service_adapter=adapter)

        self.assertEqual(len(result.acknowledgements), 1)
        ack = result.acknowledgements[0]
        self.assertEqual(ack.message_id, "ack-Sensor-A-1234")
        self.assertEqual(ack.device_id, "Sensor-A")
        self.assertEqual(ack.timestamp, 1234)
        self.assertEqual(ack.status, "DELIVERED")
        self.assertTrue(ack.is_delivered())

    # 17. Adapter failure behavior (pipeline never silently marks failed submissions as delivered)
    def test_adapter_failure_behavior(self) -> None:
        """Verify that adapter reporting failure or raising exception records failed deliveries."""
        # 17.1 Adapter configured to fail on a specific device
        selective_adapter = InMemoryServiceAdapter(fail_on_device="Device-FAIL")
        inputs = [
            {"device_id": "Device-OK", "timestamp": 1, "reading": 10},
            {"device_id": "Device-FAIL", "timestamp": 2, "reading": 20},
        ]
        result = process_message_stream(inputs, service_adapter=selective_adapter)
        self.assertTrue(verify_pipeline_contract(inputs, result, adapter=selective_adapter))

        # Both were accepted
        self.assertEqual(len(result.accepted), 2)
        # Only Device-OK is delivered
        self.assertEqual(len(result.delivered), 1)
        self.assertEqual(result.delivered[0]["device_id"], "Device-OK")
        # Device-FAIL is in failed_deliveries
        self.assertEqual(len(result.failed_deliveries), 1)
        self.assertEqual(
            result.failed_deliveries[0]["message"]["device_id"], "Device-FAIL"
        )
        self.assertEqual(
            result.failed_deliveries[0]["acknowledgement"].status, "FAILED"
        )

        # 17.2 Adapter callable that raises an unhandled exception
        def crashing_adapter(msg):
            raise ConnectionError("Network unreachable")

        crash_result = process_message_stream(
            [{"device_id": "Dev", "timestamp": 1, "reading": 10}],
            service_adapter=crashing_adapter,
        )
        self.assertEqual(len(crash_result.delivered), 0)
        self.assertEqual(len(crash_result.failed_deliveries), 1)
        self.assertIn(
            "unreachable",
            crash_result.failed_deliveries[0]["acknowledgement"].details,
        )

    # 18. Empty input
    def test_empty_input(self) -> None:
        """Verify that processing an empty input stream produces empty results and satisfies contract."""
        adapter = InMemoryServiceAdapter()
        result = process_message_stream([], service_adapter=adapter)
        self.assertTrue(verify_pipeline_contract([], result, adapter=adapter))
        self.assertEqual(len(result.accepted), 0)
        self.assertEqual(len(result.duplicates), 0)
        self.assertEqual(len(result.rejected), 0)
        self.assertEqual(len(result.delivered), 0)
        self.assertEqual(len(result.failed_deliveries), 0)

    # 19. Deliberate contract failure detection
    def test_deliberate_contract_failure_detection(self) -> None:
        """Verify that contract verifier catches corrupted results and raises AssertionError."""
        fixture = get_required_fixture()
        adapter = InMemoryServiceAdapter()
        clean_result = process_message_stream(fixture, service_adapter=adapter)

        # 19.1 Falsely mark a failed delivery as delivered
        failing_adapter = InMemoryServiceAdapter(should_fail=True)
        fail_result = process_message_stream(fixture, service_adapter=failing_adapter)
        # Tamper: falsely inject an accepted message into delivered
        corrupt_delivered = deepcopy(fail_result)
        corrupt_delivered.delivered.append(corrupt_delivered.accepted[0])
        with self.assertRaises(AssertionError) as ctx:
            verify_pipeline_contract(fixture, corrupt_delivered)
        self.assertTrue(
            "marked as delivered" in str(ctx.exception).lower()
            or "total delivery outcomes" in str(ctx.exception).lower()
        )

        # 19.2 Invert chronological ordering of accepted messages
        corrupt_order = deepcopy(clean_result)
        corrupt_order.accepted.reverse()
        with self.assertRaises(AssertionError) as ctx:
            verify_pipeline_contract(fixture, corrupt_order)
        self.assertIn("sorting rule", str(ctx.exception).lower())

        # 19.3 Inconsistent classification count
        corrupt_counts = deepcopy(clean_result)
        corrupt_counts.accepted.pop()
        with self.assertRaises(AssertionError) as ctx:
            verify_pipeline_contract(fixture, corrupt_counts)
        self.assertIn("total classified messages", str(ctx.exception).lower())

    # 20. Adapter returns None
    def test_adapter_returns_none(self) -> None:
        """Verify that an adapter returning None is treated as failed delivery with descriptive details."""
        def none_adapter(msg):
            return None

        inputs = [{"device_id": "Device-None", "timestamp": 10, "reading": 5}]
        result = process_message_stream(inputs, service_adapter=none_adapter)
        self.assertTrue(verify_pipeline_contract(inputs, result))

        self.assertEqual(len(result.accepted), 1)
        self.assertEqual(len(result.delivered), 0)
        self.assertEqual(len(result.failed_deliveries), 1)
        ack = result.acknowledgements[0]
        self.assertEqual(ack.status, "FAILED")
        self.assertIn("expected serviceacknowledgement", ack.details.lower())
        self.assertIn("nonetype", ack.details.lower())

    # 21. Adapter returns a string
    def test_adapter_returns_string(self) -> None:
        """Verify that an adapter returning a string is treated as failed delivery with descriptive details."""
        def string_adapter(msg):
            return "SUCCESS_OK"

        inputs = [{"device_id": "Device-Str", "timestamp": 20, "reading": 15}]
        result = process_message_stream(inputs, service_adapter=string_adapter)
        self.assertTrue(verify_pipeline_contract(inputs, result))

        self.assertEqual(len(result.accepted), 1)
        self.assertEqual(len(result.delivered), 0)
        self.assertEqual(len(result.failed_deliveries), 1)
        ack = result.acknowledgements[0]
        self.assertEqual(ack.status, "FAILED")
        self.assertIn("expected serviceacknowledgement", ack.details.lower())
        self.assertIn("str", ack.details.lower())

    # 22. Adapter returns a ServiceAcknowledgement with an invalid status
    def test_adapter_returns_invalid_status(self) -> None:
        """Verify that an acknowledgement with unsupported status is treated as failed delivery."""
        def invalid_status_adapter(msg):
            return ServiceAcknowledgement(
                message_id="ack-invalid",
                device_id=msg["device_id"],
                timestamp=msg["timestamp"],
                status="PENDING",  # invalid status (only DELIVERED and FAILED allowed)
                details="Queued in staging.",
            )

        inputs = [{"device_id": "Device-Pending", "timestamp": 30, "reading": 25}]
        result = process_message_stream(inputs, service_adapter=invalid_status_adapter)
        self.assertTrue(verify_pipeline_contract(inputs, result))

        self.assertEqual(len(result.accepted), 1)
        self.assertEqual(len(result.delivered), 0)
        self.assertEqual(len(result.failed_deliveries), 1)
        ack = result.acknowledgements[0]
        self.assertEqual(ack.status, "FAILED")
        self.assertIn("expected 'delivered' or 'failed'", ack.details.lower())
        self.assertIn("'pending'", ack.details.lower())


if __name__ == "__main__":
    unittest.main()
