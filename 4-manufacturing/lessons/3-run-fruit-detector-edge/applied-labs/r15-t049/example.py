"""Fictional fruit-detector-edge threat scenarios: STRUCTURE-ONLY rubric.

PASS only means nonblank fields and matching author-supplied topic tags.
A human must assess whether controls mitigate threats; NO real edge inference occurs.
"""

FIELDS = ("asset", "threat", "control", "residual_risk")
TAGS = ("integrity", "privacy", "availability")
SCENARIOS = {
    "Altered edge model package": {
        "asset": "Integrity of a fictional fruit classifier package deployed at the edge.",
        "threat": "[integrity] A modified model package could alter local classification results.",
        "control": "[integrity] Verify an approved package checksum before using the package.",
        "residual_risk": "An approved but faulty package might still make mistakes.",
    },
    "Exposed fruit camera frame": {
        "asset": "Privacy of a fictional image captured near workers.",
        "threat": "[privacy] A local operator may view sensitive frame contents.",
        "control": "[privacy] Restrict access to locally stored frames.",
        "residual_risk": "An authorized operator might still misuse an image.",
    },
    "Offline classifier interruption": {
        "asset": "Availability of a fictional local fruit-sorter response.",
        "threat": "[availability] A local edge process stops responding to requests.",
        "control": "[availability] Send a clear unavailable status and require an operator check.",
        "residual_risk": "Sorting can remain unavailable until manual intervention.",
    },
}


def check_scenario(scenario):
    """Check field structure + tag overlap ONLY, never explanation correctness."""
    if not isinstance(scenario, dict):
        return ("FAIL", "scenario must be an object")
    missing = [name for name in FIELDS if not isinstance(scenario.get(name), str)
               or not scenario[name].strip()]
    if missing:
        return ("FAIL", "missing/blank: " + ",".join(missing))
    def tags(text):
        return {name for name in TAGS if "[" + name + "]" in text.lower()}
    if not (tags(scenario["threat"]) & tags(scenario["control"])):
        return ("REVIEW", "threat/control topic tags differ; human review required")
    return ("PASS", "four fields supplied and matching author tag; human review still required")


def failure_and_recovery():
    """One missing-data failure, then a fresh valid input accepted."""
    invalid = dict(SCENARIOS["Altered edge model package"])
    del invalid["asset"]
    return check_scenario(invalid), check_scenario(SCENARIOS["Altered edge model package"])


def main():
    print("FICTIONAL edge-fruit scenarios: STRUCTURE-ONLY, not correctness")
    for name, scenario in SCENARIOS.items():
        print("{}: {}".format(name, check_scenario(scenario)[0]))
    failed, recovered = failure_and_recovery()
    print("missing_asset: {} ({})".format(*failed))
    print("next_valid_input: {} ({})".format(*recovered))
    unmatched = dict(SCENARIOS["Altered edge model package"])
    unmatched["control"] = "[privacy] Hide image previews from visitors."
    print("unrelated_control: {} ({})".format(*check_scenario(unmatched)))


if __name__ == "__main__":
    main()
