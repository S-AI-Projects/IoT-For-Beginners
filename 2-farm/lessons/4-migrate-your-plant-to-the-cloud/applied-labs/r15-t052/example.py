import json
import math
from typing import Any


def _is_valid_pixel(value: Any) -> bool:
    """Return True if value is a finite int/float in [0, 255] (excluding bool)."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return False
    if not math.isfinite(value):
        return False
    return 0 <= value <= 255


def validate_and_normalize_batch(batch: Any) -> dict[str, Any]:
    """
    Validate an N x H x W synthetic image batch with pixels in 0..255
    and normalize values to 0..1 without changing the batch shape.
    """
    if not isinstance(batch, list) or len(batch) == 0:
        raise ValueError("Batch must be a non-empty 3D list (N x H x W).")

    n = len(batch)
    if not isinstance(batch[0], list) or len(batch[0]) == 0:
        raise ValueError("Each image in batch must have non-zero height H.")
    h = len(batch[0])

    if not isinstance(batch[0][0], list) or len(batch[0][0]) == 0:
        raise ValueError("Each image row must have non-zero width W.")
    w = len(batch[0][0])

    normalized: list[list[list[float]]] = []
    for i, image in enumerate(batch):
        if not isinstance(image, list) or len(image) != h:
            raise ValueError(f"Inconsistent height at batch index {i}: expected {h}.")
        norm_image: list[list[float]] = []
        for r, row in enumerate(image):
            if not isinstance(row, list) or len(row) != w:
                raise ValueError(f"Inconsistent width at image {i}, row {r}: expected {w}.")
            norm_row: list[float] = []
            for c, pixel in enumerate(row):
                if not _is_valid_pixel(pixel):
                    raise ValueError(
                        f"Invalid pixel {pixel!r} at ({i}, {r}, {c}): must be numeric in 0..255."
                    )
                norm_row.append(round(pixel / 255.0, 6))
            norm_image.append(norm_row)
        normalized.append(norm_image)

    return {
        "shape": [n, h, w],
        "normalized": normalized,
    }


if __name__ == "__main__":
    sample_batch = [[[0, 255], [128, 64]]]
    result = validate_and_normalize_batch(sample_batch)
    print(json.dumps(result, indent=2))
