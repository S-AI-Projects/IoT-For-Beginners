# R15-T052: Tensor-Shape Contract — Boundary-Case Lesson Extension

## Overview & Lesson Connection
This local simulation example illustrates the input validation and pixel-normalization preprocessing contract that occurs before sending plant camera frames to a cloud inference service in **Migrate your plant to the cloud**.

- **What it illustrates:** Enforcing a strict N x H x W tensor shape contract, validating pixel bounds (`0..255` inclusive), and rescaling numeric pixel intensities into `[0.0, 1.0]` (`0 -> 0.0`, `255 -> 1.0`) without altering batch dimensions.
- **Where simplifications stop:** This example uses small synthetic 3D lists in Python standard library (`0` external dependencies). It does **not** connect to Azure IoT Hub / Custom Vision, download trained models, use a GPU, or read physical camera hardware.

## Boundary Decisions
- **Valid range:** Finite `int` or `float` pixels where `0 <= pixel <= 255` (booleans are explicitly rejected).
- **Smallest boundary fixture:** `[[[0, 255], [128, 64]]]` (shape `[1, 2, 2]`), testing both exact lower (`0 -> 0.0`) and upper (`255 -> 1.0`) boundaries alongside interior values (`128`, `64`).
- **Invalid cases rejected (`ValueError`):** Negative pixels (`-1`), out-of-range pixels (`256`), ragged row/image dimensions, empty dimensions, booleans, `NaN`/`Inf`, and non-numeric values.

## Exact Invocation
    python3 2-farm/lessons/4-migrate-your-plant-to-the-cloud/applied-labs/r15-t052/example.py

## Run Unit Tests
    python3 -m unittest discover -v -s 2-farm/lessons/4-migrate-your-plant-to-the-cloud/applied-labs/r15-t052 -p "test_*.py"
