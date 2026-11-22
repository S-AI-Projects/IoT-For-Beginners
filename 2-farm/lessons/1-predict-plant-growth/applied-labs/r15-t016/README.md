# Applied Lab: Growing-Degree Calculation — Refactor the Teaching Example (R15-T016)

This lab extends the [Predict Plant Growth with IoT lesson](../../README.md) by demonstrating clean code refactoring, input validation, and thermal time accumulation using Growing Degree Days (GDD).

## Concept & Curriculum Connection

In precision agriculture, temperature sensors monitor ambient conditions to estimate crop maturation timelines. Growing Degree Days (GDD) represent the amount of heat accumulated above a specific base biological threshold:
$$\text{daily\_gdd} = \max\left(0, \frac{T_{\min} + T_{\max}}{2} - T_{\text{base}}\right)$$
$$\text{total\_gdd} = \sum_{d=1}^{N} \text{daily\_gdd}_d$$

### Validation & Domain Invariants
- **Domain Sanity:** Minimum temperature cannot exceed maximum temperature ($T_{\min} \le T_{\max}$). Any record violating this raises a `ValueError`.
- **Non-Negative Contribution:** Heat units never accumulate negatively; days with average temperatures below $T_{\text{base}}$ contribute $0$.

## Refactoring Focus
1. **Baseline (`calculate_gdd_baseline`):** Monolithic loop coupling input validation, daily mean computation, floor clamping, and accumulator state.
2. **Extracted Responsibility (`compute_single_day_gdd`):** Isolates the calculation and validation for a single daily interval into an independently testable function.
3. **Equivalence:** The test suite mathematically proves equivalence between the baseline and refactored versions across all test cases.

## Benchmark Fixture
- Base temperature: $10.0^\circ\text{C}$
- Daily records: `[(8, 16), (12, 20), (2, 8)]`
- Calculation breakdown:
  - Day 1: $\max(0, (8+16)/2 - 10) = 12 - 10 = 2.0$
  - Day 2: $\max(0, (12+20)/2 - 10) = 16 - 10 = 6.0$
  - Day 3: $\max(0, (2+8)/2 - 10) = \max(0, 5 - 10) = 0.0$
  - Total: $2.0 + 6.0 + 0.0 = 8.0$

## Verification & Execution

Prerequisites: Python 3 standard library.

### Run Example
```bash
python3 2-farm/lessons/1-predict-plant-growth/applied-labs/r15-t016/example.py
```

### Run Tests
```bash
python3 -m unittest discover -s 2-farm/lessons/1-predict-plant-growth/applied-labs/r15-t016 -p "test_*.py"
```

## Simulation Scope & Limitations
- **Local Arithmetic:** Focuses on computational correctness and software refactoring patterns.
- **Hardware Boundary:** Does not interact with physical soil temperature probes or cloud weather APIs.
