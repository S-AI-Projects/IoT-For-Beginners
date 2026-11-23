# R15-T049 — Fictional edge-classifier security scenarios and recovery

This **fictional**, entirely offline exercise illustrates why the [edge fruit detector lesson](../../README.md) must consider the integrity, privacy and availability of locally handled components. No fruit images, model artifacts, hardware, containers or network services are involved.

All three scenarios use exactly four textual fields (`asset`, `threat`, `control`, `residual_risk`): **Altered edge model package**, **Exposed fruit camera frame**, **Offline classifier interruption**.

Run from the repository root:

```sh
python3 4-manufacturing/lessons/3-run-fruit-detector-edge/applied-labs/r15-t049/example.py
python3 -m unittest discover -s 4-manufacturing/lessons/3-run-fruit-detector-edge/applied-labs/r15-t049 -p "test_*.py"
```

Expected statuses: the three complete fictional scenarios `PASS`; missing asset `FAIL`; the **next valid** scenario `PASS` (recovery); mismatched threat/control topic tags `REVIEW` (not automatically failed). Missing or whitespace-only fields are rejected, but processing subsequent valid inputs works without restarting the process.

The rubric verifies **structure only**, plus a mechanical match of author-provided `[integrity]`, `[privacy]` or `[availability]` text tags. A `PASS` **does not mean** a proposed security control is correct, sufficient or effective; a human reviewer must assess its relevance and explanation. A `REVIEW` flag is not an automated correctness judgment.

Run `RUN_INTENTIONAL_FAILURE=1 python3 -m unittest discover -s 4-manufacturing/lessons/3-run-fruit-detector-edge/applied-labs/r15-t049 -p "test_*.py"` to confirm an intentionally wrong expectation causes a nonzero exit. This example does not establish any real edge behavior, cloud performance, security assurance or ML classification quality.
