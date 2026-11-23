# R15-T046 — Baseline and schema-validation refactor

This example connects the named lesson to **fictional, local JSON sensor-message records**. It is **not** a reading from a camera, microphone, real IoT device, classifier, cloud service, or model. Python 3 standard library only.

`baseline` validates each input inline. The refactored `process` calls a separately named `validate` responsibility for JSON parsing and field checks, keeping duplicate detection and sorting in `process`.

From the repository root:

```sh
python3 1-getting-started/lessons/3-sensors-and-actuators/applied-labs/r15-t046/example.py
python3 -m unittest discover -s 1-getting-started/lessons/3-sensors-and-actuators/applied-labs/r15-t046 -p "test_*.py"
```

Input fixture (JSON text): `A@2` reading `10.5`, `A@1` reading `8`, duplicate `A@1` reading `999`, and `A@3` reading `"bad"`. Expected core output:

```text
accepted=[A@1,A@2] rejected=[2:duplicate_device_timestamp,3:invalid_reading]
```

The first valid record for a device/timestamp pair wins. Each accepted message requires a nonblank `device_id`, integer `timestamp`, and finite numeric `reading` (not `bool`). Rejected messages report zero-based input indices; accepted messages are sorted by timestamp, then device ID.

The script prints both `before:` and `after:` reports followed by `equal=true`. Tests compare exact acceptance, rejection and ordering before versus after on normal, empty, malformed and multi-device fixtures. This is an offline teaching refactor, not a hardware change.

To confirm a wrong answer causes a nonzero test exit, run:

```sh
RUN_INTENTIONAL_FAILURE=1 python3 -m unittest discover -s 1-getting-started/lessons/3-sensors-and-actuators/applied-labs/r15-t046 -p "test_*.py"
```

This local fixture does not demonstrate delivery reliability, service authentication, sensor calibration, classifier accuracy, audio transcription, or any other real-system behavior.
