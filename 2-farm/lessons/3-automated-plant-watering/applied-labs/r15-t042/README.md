# R15-T042 — Moisture hysteresis boundary cases

This self-contained **fictional** example complements the lesson's discussion of delayed sensor response and actuator timing. It uses no sensor, pump, relay, MQTT broker or cloud service.

From the repository root:

```sh
python3 2-farm/lessons/3-automated-plant-watering/applied-labs/r15-t042/example.py
python3 -m unittest discover -s 2-farm/lessons/3-automated-plant-watering/applied-labs/r15-t042 -p "test_*.py"
```

With the pump initially off, readings `[700,250,400,650]` yield `off,on,on,off`. Strict boundaries at `300` and `600` retain the previous state. The smallest and largest allowed readings are `0` and `1023`; other values, booleans and non-integers are rejected.

The script prints `states=off,on,on,off`, `boundary: 300 with on -> on`, `boundary: 600 with off -> off`, and `invalid 1024 -> rejected: moisture must be an integer in 0..1023`.

To verify a deliberately incorrect expected answer causes a failure, run `RUN_INTENTIONAL_FAILURE=1 python3 -m unittest discover -s 2-farm/lessons/3-automated-plant-watering/applied-labs/r15-t042 -p "test_*.py"`; this must exit nonzero. This example does not establish any real moisture calibration, timing, device reliability or safe pump operation.
