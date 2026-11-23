# R15-T044 — Invariant and state trace

This example connects the named lesson to **fictional, local JSON sensor-message records**. It is **not** a reading from a camera, microphone, real IoT device, classifier, cloud service, or model. Python 3 standard library only.

The trace records accepted and rejected counts plus accepted `(device_id, timestamp)` keys after **each** input. The invariant is `accepted_count + rejected_count == processed_steps` and unique accepted keys match the final result.

From the repository root:

```sh
python3 1-getting-started/lessons/1-introduction-to-iot/applied-labs/r15-t044/example.py
python3 -m unittest discover -s 1-getting-started/lessons/1-introduction-to-iot/applied-labs/r15-t044 -p "test_*.py"
```

Input fixture (JSON text): `A@2` reading `10.5`, `A@1` reading `8`, duplicate `A@1` reading `999`, and `A@3` reading `"bad"`. Expected core output:

```text
accepted=[A@1,A@2] rejected=[2:duplicate_device_timestamp,3:invalid_reading]
```

The first valid record for a device/timestamp pair wins. Each accepted message requires a nonblank `device_id`, integer `timestamp`, and finite numeric `reading` (not `bool`). Rejected messages report zero-based input indices; accepted messages are sorted by timestamp, then device ID.

The trace count progression is `(1,0)`, `(2,0)`, `(2,1)`, `(2,2)` for accepted/rejected. Sorting is performed after validation.

To confirm a wrong answer causes a nonzero test exit, run:

```sh
RUN_INTENTIONAL_FAILURE=1 python3 -m unittest discover -s 1-getting-started/lessons/1-introduction-to-iot/applied-labs/r15-t044 -p "test_*.py"
```

This local fixture does not demonstrate delivery reliability, service authentication, sensor calibration, classifier accuracy, audio transcription, or any other real-system behavior.
