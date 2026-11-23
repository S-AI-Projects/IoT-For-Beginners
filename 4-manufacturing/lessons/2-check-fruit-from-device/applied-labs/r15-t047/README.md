# R15-T047 — Worked input-to-output example and regression

This example connects the named lesson to **fictional, local JSON sensor-message records**. It is **not** a reading from a camera, microphone, real IoT device, classifier, cloud service, or model. Python 3 standard library only.

This is a **local message-validation illustration** alongside the lesson about fruit-image classification. It does not analyze photos, call a classifier or establish any predicted label.

From the repository root:

```sh
python3 4-manufacturing/lessons/2-check-fruit-from-device/applied-labs/r15-t047/example.py
python3 -m unittest discover -s 4-manufacturing/lessons/2-check-fruit-from-device/applied-labs/r15-t047 -p "test_*.py"
```

Input fixture (JSON text): `A@2` reading `10.5`, `A@1` reading `8`, duplicate `A@1` reading `999`, and `A@3` reading `"bad"`. Expected core output:

```text
accepted=[A@1,A@2] rejected=[2:duplicate_device_timestamp,3:invalid_reading]
```

The first valid record for a device/timestamp pair wins. Each accepted message requires a nonblank `device_id`, integer `timestamp`, and finite numeric `reading` (not `bool`). Rejected messages report zero-based input indices; accepted messages are sorted by timestamp, then device ID.

Worked steps for the four fixture inputs: `0: accept A@2`, `1: accept A@1`, `2: reject duplicate_device_timestamp`, `3: reject invalid_reading`, then sort accepted records into `A@1,A@2`. The exact five-line result is asserted as a regression test.

To confirm a wrong answer causes a nonzero test exit, run:

```sh
RUN_INTENTIONAL_FAILURE=1 python3 -m unittest discover -s 4-manufacturing/lessons/2-check-fruit-from-device/applied-labs/r15-t047 -p "test_*.py"
```

This local fixture does not demonstrate delivery reliability, service authentication, sensor calibration, classifier accuracy, audio transcription, or any other real-system behavior.
