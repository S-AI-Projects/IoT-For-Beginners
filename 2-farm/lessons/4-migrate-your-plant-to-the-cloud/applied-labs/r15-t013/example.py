"""
Tensor-Shape Contract & Image Batch Normalization (R15-T013)

Lesson reference: 2-farm/lessons/4-migrate-your-plant-to-the-cloud/README.md
Concept: Before sending camera sensor frames to cloud image classification models,
the edge preprocessor must validate the batch tensor shape (N×H×W) and normalize pixel
intensities from uint8 [0..255] to float [0..1] without altering tensor dimensionality.

Contracts:
1. Accepts 3D tensor batch of shape N×H×W with numeric pixel values.
2. Value range: 0 <= pixel <= 255.
3. Reject negative pixels or pixels > 255.
4. Output maintains exact (N, H, W) shape, mapping 0 -> 0.0 and 255 -> 1.0.
5. Verifies preprocessing only; makes no claim on model accuracy or cloud latency.
"""

from typing import Any, List, Tuple


def get_shape(batch: Any) -> Tuple[int, int, int]:
    """Validates that batch is a regular 3D list (N x H x W) and returns its shape."""
    if not isinstance(batch, list) or len(batch) == 0:
        raise ValueError("Batch must be a non-empty list representing N samples")

    n = len(batch)
    if not isinstance(batch[0], list) or len(batch[0]) == 0:
        raise ValueError("Each sample in batch must be a non-empty 2D matrix (H rows)")

    h = len(batch[0])
    if not isinstance(batch[0][0], list) or len(batch[0][0]) == 0:
        raise ValueError("Each row in sample must be a non-empty list of W pixels")

    w = len(batch[0][0])

    for i, sample in enumerate(batch):
        if not isinstance(sample, list) or len(sample) != h:
            raise ValueError(f"Inconsistent height at sample {i}: expected {h}, got {len(sample) if isinstance(sample, list) else 'non-list'}")
        for j, row in enumerate(sample):
            if not isinstance(row, list) or len(row) != w:
                raise ValueError(f"Inconsistent width at sample {i}, row {j}: expected {w}, got {len(row) if isinstance(row, list) else 'non-list'}")

    return (n, h, w)


def validate_and_normalize_direct(batch: List[List[List[float]]]) -> Tuple[Tuple[int, int, int], List[List[List[float]]]]:
    """
    Direct implementation: Iterates through each pixel, validates boundaries [0..255],
    and normalizes to [0.0..1.0].
    """
    shape = get_shape(batch)
    normalized = []
    for sample in batch:
        norm_sample = []
        for row in sample:
            norm_row = []
            for p in row:
                if isinstance(p, bool) or not isinstance(p, (int, float)):
                    raise TypeError(f"Pixel value {p} is not numeric")
                if p < 0 or p > 255:
                    raise ValueError(f"Pixel value {p} out of range [0, 255]")
                norm_row.append(p / 255.0)
            norm_sample.append(norm_row)
        normalized.append(norm_sample)
    return shape, normalized


def reference_independent_normalize(batch: List[List[List[float]]]) -> Tuple[Tuple[int, int, int], List[List[List[float]]]]:
    """
    Independent reference approach: Precomputes expected table/mapping and flattens checks
    for cross-validation against the direct implementation.
    """
    shape = get_shape(batch)
    # Validate all elements first
    for sample in batch:
        for row in sample:
            for p in row:
                if isinstance(p, bool) or not isinstance(p, (int, float)):
                    raise TypeError(f"Pixel value {p} is not numeric")
                if p < 0 or p > 255:
                    raise ValueError(f"Pixel value {p} out of range [0, 255]")

    # Independent list comprehension mapping
    norm = [[[round(val / 255.0, 6) for val in row] for row in sample] for sample in batch]
    return shape, norm


def run_demo():
    fixture = [[[0, 255], [128, 64]]]
    shape, norm = validate_and_normalize_direct(fixture)
    print(f"Input fixture shape: {shape}")
    print(f"Normalized output: {norm}")
    return shape, norm


if __name__ == "__main__":
    run_demo()
