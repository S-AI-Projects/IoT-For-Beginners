# R15-T034: tensor-shape contract with an offline service adapter

Extends the [Migrate your plant to the cloud](../../README.md) lesson. The lesson
sends data from a device to a cloud service; this example shows the checking you
do *before* sending, on a synthetic image batch.

**Scope:** a local simulation in standard-library Python 3. No cloud service,
model download, paid provider, GPU or device. It checks **preprocessing only,
not model quality**. The lesson itself covers IoT Hub, not image tensors, so this
is an applied extension and its simplifications are listed below.

## Contract

- Input: a batch of N images, each H rows of W pixels (shape N x H x W), numbers 0..255.
- `normalize_batch` returns the same shape with each value divided by 255, so 0..1.
- Negative pixels, pixels above 255, non-numbers, empty or ragged batches raise `ValueError`.

## Service behind a callable

`run(batch, service)` validates and normalizes, then calls `service(normalized_batch)`,
which returns one result per image. `LocalAdapter` is a deterministic stand-in
(mean pixel above 0.5 gives `bright`, otherwise `dark`).

**What the mock does not establish about a real service:** authentication, network
latency and failures, rate limits, the real request and response format, payload
size limits, or any model accuracy.

## Fixture

| Input | Output |
|---|---|
| `[[[0,255],[128,64]]]` (1x2x2) | shape stays (1,2,2); 0 gives 0, 255 gives 1, 128 gives 128/255 (about 0.502), 64 gives 64/255 (about 0.251) |
| a pixel of -1 | `ValueError` |
| a pixel of 256 | `ValueError` |

## Run

```
python3 2-farm/lessons/4-migrate-your-plant-to-the-cloud/applied-labs/r15-t034/example.py
python3 -m unittest discover -s 2-farm/lessons/4-migrate-your-plant-to-the-cloud/applied-labs/r15-t034 -p "test_*.py"
```
