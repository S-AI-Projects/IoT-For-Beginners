# R15-T048 — Three-size offline evaluation

This example connects the named lesson to **fictional, local JSON sensor-message records**. It is **not** a reading from a camera, microphone, real IoT device, classifier, cloud service, or model. Python 3 standard library only.

The controlled input sizes are 4, 8 and 16 records (1, 2 and 4 unique device groups). Each group has two accepted, one duplicate and one nonnumeric record. The metric is **exact count agreement** with a hand-defined fixture plus the **accepted fraction**, not elapsed time or prediction accuracy.

From the repository root:

```sh
python3 6-consumer/lessons/1-speech-recognition/applied-labs/r15-t048/example.py
python3 -m unittest discover -s 6-consumer/lessons/1-speech-recognition/applied-labs/r15-t048 -p "test_*.py"
```

Input fixture (JSON text): `A@2` reading `10.5`, `A@1` reading `8`, duplicate `A@1` reading `999`, and `A@3` reading `"bad"`. Expected core output:

```text
accepted=[A@1,A@2] rejected=[2:duplicate_device_timestamp,3:invalid_reading]
```

The first valid record for a device/timestamp pair wins. Each accepted message requires a nonblank `device_id`, integer `timestamp`, and finite numeric `reading` (not `bool`). Rejected messages report zero-based input indices; accepted messages are sorted by timestamp, then device ID.

Observed deterministic results: `4 -> accepted=2 rejected=2`, `8 -> 4/4`, `16 -> 8/8`; all have `acceptance_fraction=0.50` and `correct=True`. As inputs increase, the **absolute number of checks/records grows**, while the acceptance fraction stays constant by construction. This says nothing about runtime scaling, recognition/model quality, network latency or production throughput.

To confirm a wrong answer causes a nonzero test exit, run:

```sh
RUN_INTENTIONAL_FAILURE=1 python3 -m unittest discover -s 6-consumer/lessons/1-speech-recognition/applied-labs/r15-t048 -p "test_*.py"
```

This local fixture does not demonstrate delivery reliability, service authentication, sensor calibration, classifier accuracy, audio transcription, or any other real-system behavior.
