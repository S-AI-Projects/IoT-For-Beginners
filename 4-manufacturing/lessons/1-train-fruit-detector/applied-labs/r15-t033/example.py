"""Binary classification evaluation with a state trace (R15-T033).

Standard library only. A SIMULATION on fixed labels: no model, Custom Vision
service, image or hardware is used, and nothing here measures a trained model.

Label order: y_true first, y_pred second. Positive class = 1, negative = 0.
Zero-denominator policy: if the denominator of a ratio is 0, the ratio is
defined as 0.0 (precision when there are no predicted positives, recall when
there are no actual positives).
"""


def evaluate(y_true, y_pred):
    """Return (result, trace).

    trace is a list of dicts: the counts after each processed pair.
    result has tp, fn, fp, tn, precision, recall.
    """
    if len(y_true) != len(y_pred):
        raise ValueError("y_true and y_pred must have the same length")
    for v in list(y_true) + list(y_pred):
        if v not in (0, 1) or isinstance(v, bool):
            raise ValueError("labels must be 0 or 1, got %r" % (v,))

    tp = fn = fp = tn = 0
    trace = []
    for i, (t, p) in enumerate(zip(y_true, y_pred), start=1):
        if t == 1 and p == 1:
            tp += 1
        elif t == 1 and p == 0:
            fn += 1
        elif t == 0 and p == 1:
            fp += 1
        else:
            tn += 1
        trace.append({"step": i, "tp": tp, "fn": fn, "fp": fp, "tn": tn})

    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    result = {"tp": tp, "fn": fn, "fp": fp, "tn": tn,
              "precision": precision, "recall": recall}
    return result, trace


def check_invariant(result, trace, n):
    """tp+fn+fp+tn == n after every step i, the sum equals i, and the
    final trace entry equals the result counts."""
    for entry in trace:
        if entry["tp"] + entry["fn"] + entry["fp"] + entry["tn"] != entry["step"]:
            return False
    last = trace[-1] if trace else {"tp": 0, "fn": 0, "fp": 0, "tn": 0}
    same = all(last[k] == result[k] for k in ("tp", "fn", "fp", "tn"))
    return same and result["tp"] + result["fn"] + result["fp"] + result["tn"] == n


if __name__ == "__main__":
    y_true, y_pred = [1, 1, 0, 0], [1, 0, 1, 0]
    result, trace = evaluate(y_true, y_pred)
    for entry in trace:
        print(entry)
    print(result)
    print("invariant holds:", check_invariant(result, trace, len(y_true)))
