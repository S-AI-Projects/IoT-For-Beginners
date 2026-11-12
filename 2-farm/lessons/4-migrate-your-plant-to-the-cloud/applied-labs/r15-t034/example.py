"""Tensor-shape contract with an offline service adapter (R15-T034).

Standard library only. A SIMULATION: no cloud service, model, GPU or device.

Contract: a batch is N x H x W nested lists of numbers in 0..255.
normalize_batch returns the same N x H x W shape with values in 0..1
(value / 255). Anything else raises ValueError.

The external dependency (a cloud image service) sits behind a callable
interface: service(normalized_batch) -> list of N results. LocalAdapter is a
deterministic stand-in.
"""


def batch_shape(batch):
    """Return (n, h, w). Raises ValueError if the batch is not rectangular N x H x W."""
    if not isinstance(batch, (list, tuple)) or len(batch) == 0:
        raise ValueError("batch must be a non-empty list of images")
    h = w = None
    for image in batch:
        if not isinstance(image, (list, tuple)) or len(image) == 0:
            raise ValueError("each image must be a non-empty list of rows")
        if h is None:
            h = len(image)
        elif len(image) != h:
            raise ValueError("images must all have the same height")
        for row in image:
            if not isinstance(row, (list, tuple)) or len(row) == 0:
                raise ValueError("each row must be a non-empty list of pixels")
            if w is None:
                w = len(row)
            elif len(row) != w:
                raise ValueError("rows must all have the same width")
    return len(batch), h, w


def normalize_batch(batch):
    """Validate and scale pixels from 0..255 to 0..1, keeping the shape."""
    batch_shape(batch)
    out = []
    for image in batch:
        new_image = []
        for row in image:
            new_row = []
            for px in row:
                if isinstance(px, bool) or not isinstance(px, (int, float)) or px != px:
                    raise ValueError("pixel must be a number, got %r" % (px,))
                if px < 0 or px > 255:
                    raise ValueError("pixel out of range 0..255: %r" % (px,))
                new_row.append(px / 255)
            new_image.append(new_row)
        out.append(new_image)
    return out


class LocalAdapter:
    """Deterministic stand-in for a cloud service: labels each image 'bright'
    when its mean normalized pixel is above 0.5, else 'dark'.

    What this does NOT establish about a real service: authentication, network
    latency or failures, rate limits, the real request/response format, size
    limits, or anything about model accuracy."""

    def __call__(self, normalized_batch):
        results = []
        for image in normalized_batch:
            pixels = [px for row in image for px in row]
            results.append("bright" if sum(pixels) / len(pixels) > 0.5 else "dark")
        return results


def run(batch, service):
    """Validate, normalize, then call the injected service."""
    normalized = normalize_batch(batch)
    return service(normalized)


if __name__ == "__main__":
    fixture = [[[0, 255], [128, 64]]]
    print("shape in:", batch_shape(fixture))
    norm = normalize_batch(fixture)
    print("normalized:", norm, "shape out:", batch_shape(norm))
    print("adapter:", run(fixture, LocalAdapter()))
