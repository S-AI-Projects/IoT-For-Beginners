# R15-T004: Growing-Degree-Day Calculation — Invariant & State Trace

An applied laboratory extension for the [Predict plant growth with IoT](../../README.md) lesson.

## Educational Context & Scope

Growing Degree Days (GDD) measure heat accumulation over time to predict agricultural growth stages (e.g. flowering, fruit maturity). Daily accumulation follows:
$$\text{GDD} = \max\left(0, \frac{T_{\text{min}} + T_{\text{max}}}{2} - T_{\text{base}}\right)$$

This lab computes daily GDD contributions and cumulative heat units, recording an explicit intermediate execution trace after each step. It verifies loop invariants linking intermediate state to the final total and rejects physically invalid sensor readings where $T_{\text{min}} > T_{\text{max}}$.

**Scope:** Python 3 standard library simulation. No physical thermometers or cloud agronomy APIs required.

## Run

```bash
python3 2-farm/lessons/1-predict-plant-growth/applied-labs/r15-t004/example.py
python3 -m unittest discover -s 2-farm/lessons/1-predict-plant-growth/applied-labs/r15-t004 -p "test_*.py"
```

## Trace Walkthrough (Base = 10°C)

| Day | $(T_{\text{min}}, T_{\text{max}})$ | Mean Temp | Calculation | Daily GDD | Accumulated GDD | Invariant Check |
|---|---|---|---|---|---|---|
| 1 | $(8, 16)$ | 12.0°C | $12.0 - 10 = 2.0$ | 2.0 | 2.0 | $2.0 = \sum_{i=1}^1 d_i$ |
| 2 | $(12, 20)$ | 16.0°C | $16.0 - 10 = 6.0$ | 6.0 | 8.0 | $8.0 = \sum_{i=1}^2 d_i$ |
| 3 | $(2, 8)$ | 5.0°C | $5.0 - 10 = -5.0 \to 0$ | 0.0 | 8.0 | $8.0 = \sum_{i=1}^3 d_i$ |

**Total Accumulated GDD:** **8.0**

## Boundary & Error Cases

- **$T_{\text{min}} > T_{\text{max}}$:** Physical impossibility (e.g. min 25°C, max 20°C); raises `ValueError`.
- **$T_{\text{min}} = T_{\text{max}}$:** Valid boundary (e.g. constant temperature chamber); accepted.
- **Negative Effective Heat:** When daily mean is below base temperature, GDD is clamped to 0 (no negative accumulation).

## Where the Simplification Stops

Real agricultural models (e.g. modified Sine wave, Baskerville-Emin method, or upper threshold capping at 30°C to model plant heat stress) incorporate diurnal curve fitting rather than simple arithmetic averaging.
