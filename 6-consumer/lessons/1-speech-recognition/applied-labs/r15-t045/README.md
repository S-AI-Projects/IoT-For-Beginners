# R15-T045 — Offline service adapter

This example connects the named lesson to **fictional, local JSON sensor-message records**. It is **not** a reading from a camera, microphone, real IoT device, classifier, cloud service, or model. Python 3 standard library only.

The external message source is represented by a **callable interface** `run_with_source(fetch_messages)`. The supplied `local_source` adapter returns deterministic local JSON strings. The validator has no service configuration or network code.

From the repository root:

```sh
python3 6-consumer/lessons/1-speech-recognition/applied-labs/r15-t045/example.py
python3 -m unittest discover -s 6-consumer/lessons/1-speech-recognition/applied-labs/r15-t045 -p "test_*.py"
```

Input fixture (JSON text): `A@2` reading `10.5`, `A@1` reading `8`, duplicate `A@1` reading `999`, and `A@3` reading `"bad"`. Expected core output:

```text
accepted=[A@1,A@2] rejected=[2:duplicate_device_timestamp,3:invalid_reading]
```

The first valid record for a device/timestamp pair wins. Each accepted message requires a nonblank `device_id`, integer `timestamp`, and finite numeric `reading` (not `bool`). Rejected messages report zero-based input indices; accepted messages are sorted by timestamp, then device ID.

Replacing `local_source` with another callable changes only where messages come from, not validation rules. **This mock cannot establish that any real speech service, microphone, latency or authentication behaves correctly.**

To confirm a wrong answer causes a nonzero test exit, run:

```sh
RUN_INTENTIONAL_FAILURE=1 python3 -m unittest discover -s 6-consumer/lessons/1-speech-recognition/applied-labs/r15-t045 -p "test_*.py"
```

This local fixture does not demonstrate delivery reliability, service authentication, sensor calibration, classifier accuracy, audio transcription, or any other real-system behavior.
