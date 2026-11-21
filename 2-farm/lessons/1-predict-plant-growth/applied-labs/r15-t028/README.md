# Applied Lab: Growing-Degree Calculation — Failure and Recovery Example

Coursework Task: **R15-T028**
Context Lesson: `2-farm/lessons/1-predict-plant-growth`

---

## 1. Learning Objective

In digital agriculture, plant maturity and growth rate are strongly influenced by accumulated thermal time rather than calendar days. **Growing Degree Days (GDD)** quantify the amount of daily heat accumulation above a plant-specific base temperature.

IoT devices deployed in fields continuously record temperature telemetry. However, real-world sensor streams often suffer from intermittent telemetry drops (missing minimum or maximum values), inverted sensor readings, or transmission corruption.

The objective of this lab is to:
1. Implement the standard daily GDD calculation and running accumulation in pure Python.
2. Enforce strict numerical validation (rejecting missing fields, booleans, non-finite values, and inverted ranges where $T_{\min} > T_{\max}$).
3. Implement a resilient streaming pipeline that reports errors for invalid records, ensures invalid data contributes $0.0$ GDD, and seamlessly recovers when subsequent valid records arrive.

---

## 2. Formula & Units

All temperatures are measured in degrees Celsius (°C).

### Formula:
$$\text{GDD} = \max\left(0, \frac{T_{\min} + T_{\max}}{2} - T_{\text{base}}\right)$$

Where:
- $T_{\min}$: Daily minimum temperature (°C).
- $T_{\max}$: Daily maximum temperature (°C).
- $T_{\text{base}}$: Base temperature below which the plant does not grow (°C). (For this exercise, $T_{\text{base}} = 10.0^\circ\text{C}$ is an illustrative value; actual base temperatures vary by crop).
- Average temperature: $T_{\text{avg}} = \frac{T_{\min} + T_{\max}}{2}$.
- If $T_{\text{avg}} \le T_{\text{base}}$, $\text{GDD} = 0.0$ (no growth, never negative).

---

## 3. Mandatory Normal Fixture

With base temperature $T_{\text{base}} = 10.0^\circ\text{C}$, evaluate the three daily records:

| Day | $T_{\min}$ (°C) | $T_{\max}$ (°C) | $T_{\text{avg}}$ (°C) | Formula Step | Daily GDD | Running Accumulated GDD |
|:---:|:---:|:---:|:---:|:---|:---:|:---:|
| **Day 1** | 8.0 | 16.0 | 12.0 | $\max(0, 12.0 - 10.0) = 2.0$ | **2.0** | **2.0** |
| **Day 2** | 12.0 | 20.0 | 16.0 | $\max(0, 16.0 - 10.0) = 6.0$ | **6.0** | **8.0** |
| **Day 3** | 2.0 | 8.0 | 5.0 | $\max(0, 5.0 - 10.0) = \max(0, -5.0) = 0.0$ | **0.0** | **8.0** |

**Final Accumulated Total:** **8.0 GDD**

---

## 4. Failure and Recovery Fixture

Demonstrates sensor stream resilience when an intermediate reading is corrupted or incomplete:

1. **Record 1 (Valid)**: `{"minimum": 8, "maximum": 16}`
   - Outcome: Accepted. $T_{\text{avg}} = 12.0^\circ\text{C}$, Daily $\text{GDD} = 2.0$, Running Total = $2.0$.
2. **Record 2 (Missing Data Failure)**: `{"minimum": 8}` (Missing `maximum`)
   - Outcome: Rejected with clear error: `Missing required 'maximum' temperature field.`
   - Impact: Contributes $0.0$ GDD. Running Total remains preserved at $2.0$.
3. **Record 3 (Recovery)**: `{"minimum": 12, "maximum": 20}`
   - Outcome: Stream continues seamlessly. Accepted. $T_{\text{avg}} = 16.0^\circ\text{C}$, Daily $\text{GDD} = 6.0$, Running Total = $2.0 + 6.0 = 8.0$.

---

## 5. Input Validation Rules

- **Missing Fields**: Records missing either `minimum` or `maximum` (or having `None` values) are rejected.
- **Inverted Temperatures**: If $T_{\min} > T_{\max}$, the record is rejected (`Minimum temperature cannot exceed maximum temperature`). Minimum and maximum temperatures are never silently swapped.
- **Type Safety**:
  - Python `bool` values (`True`, `False`) are explicitly rejected despite being `int` subclasses.
  - Non-numeric types (strings, lists, dicts) are rejected with `TypeError`.
- **Non-Finite Values**: `NaN`, `inf`, and `-inf` are rejected with `ValueError`.
- **Stream Fault Tolerance**: Corrupt records do not terminate batch processing; they log descriptive diagnostic messages and contribute $0.0$ to the running total.

---

## 6. How to Run the CLI Scenarios

The program provides three scenarios executable in isolated processes:

### 1. Normal Scenario
Runs the mandatory 3-record fixture and verifies final accumulated total is 8.0:
```bash
python3 2-farm/lessons/1-predict-plant-growth/applied-labs/r15-t028/example.py --scenario normal
```

### 2. Boundary Scenario
Runs zero-GDD cases, inverted temperature validation, and the 3-step failure/recovery stream:
```bash
python3 2-farm/lessons/1-predict-plant-growth/applied-labs/r15-t028/example.py --scenario boundary
```

### 3. Deliberate Failure Scenario
Demonstrates intentional failure detection by asserting an invalid expected value, exiting with code 1:
```bash
python3 2-farm/lessons/1-predict-plant-growth/applied-labs/r15-t028/example.py --scenario failure
```

---

## 7. How to Run Unit Tests

Execute the test suite using Python standard-library `unittest`:

```bash
python3 -m unittest discover -s 2-farm/lessons/1-predict-plant-growth/applied-labs/r15-t028 -p "test_*.py" -v
```

---

## 8. Prerequisites and Technical Scope

- **Prerequisites**: Tested with Python 3.14.3 (standard library only; no external pip packages, MQTT clients, databases, or cloud services).
- **Scope & Limitations**:
  - This is a local mathematical simulation on synthetic temperature data.
  - It does **not** connect to real IoT temperature sensors, publish over MQTT, or write to external databases.
  - It uses a simplified average daily GDD calculation. It does not model complex agronomic factors like high-temperature heat stress cutoffs ($T_{\text{max}} > 30^\circ\text{C}$), soil temperature, photoperiod, or solar radiation.
