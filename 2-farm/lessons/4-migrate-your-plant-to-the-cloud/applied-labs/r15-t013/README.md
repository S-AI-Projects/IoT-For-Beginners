# Applied Lab: Tensor-Shape Contract & Image Batch Normalization (R15-T013)

This lab extends the [Migrate Your Plant to the Cloud lesson](../../README.md) by demonstrating image preprocessing contracts for camera-based plant monitoring systems before transferring image payloads to cloud AI endpoints.

## Concept & Curriculum Connection

In smart agriculture applications, edge devices capture soil or plant photographs to classify plant health (e.g. disease or hydration). Prior to cloud ingestion:
1. The tensor shape must be strictly validated as an $N \times H \times W$ array.
2. Pixel values in the range $[0, 255]$ must be normalized to $[0.0, 1.0]$.
3. Dimensionality must remain invariant throughout preprocessing.

> **Note on Verification vs Model Quality:** This lab verifies deterministic image preprocessing contracts, not ML model inference accuracy or training convergence.

## Contract & Rules
- **Input:** 3D array of numeric values with uniform dimensions $(N, H, W)$.
- **Bounds:** Valid pixel range is $[0, 255]$. Negative numbers or values $> 255$ raise validation errors.
- **Output:** Exact preservation of tensor shape $(N, H, W)$ with values scaled: $p_{\text{norm}} = p / 255.0$.
- **Cross-Validation:** Directly evaluates both direct and independent reference implementations on identical batches.

## Verification & Execution

Prerequisites: Python 3 standard library.

### Run Example
```bash
python3 2-farm/lessons/4-migrate-your-plant-to-the-cloud/applied-labs/r15-t013/example.py
```

### Run Tests
```bash
python3 -m unittest discover -s 2-farm/lessons/4-migrate-your-plant-to-the-cloud/applied-labs/r15-t013 -p "test_*.py"
```

## Simulation Scope & Limitations
- **Local Fixture:** Processes synthetic in-memory lists without calling Azure Custom Vision, AWS Rekognition, or requiring physical cameras.
- **Hardware Boundary:** Operates independently of real microcontrollers or edge accelerators (GPUs/NPUs).
