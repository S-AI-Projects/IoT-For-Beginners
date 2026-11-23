"""Fictional spoken-timer security scenarios and a STRUCTURE-ONLY rubric.

No audio, timer, device, cloud service, or model is used. Shared topic tags
are author-supplied labels, NOT evidence that a control works. A human must
review whether each proposed control actually addresses its threat.
"""

REQUIRED_FIELDS = ("asset", "threat", "control", "residual_risk")
TOPIC_TAGS = ("authenticity", "privacy", "integrity")

# Each named FICTIONAL fixture has exactly the four rubric fields.
# The bracketed topics are simple, inspectable metadata for the checker.
SCENARIOS = {
    "Spoofed timer completion": {
        "asset": "Trust in the timer's spoken completion announcement.",
        "threat": "[authenticity] A fictional nearby speaker impersonates a timer-complete announcement.",
        "control": "[authenticity] Announce completion only after a trusted local timer event.",
        "residual_risk": "A wrong local timer event could still produce an incorrect announcement.",
    },
    "Overheard timer feedback": {
        "asset": "Privacy of a fictional user's spoken timer label.",
        "threat": "[privacy] A bystander overhears the spoken timer label in a shared room.",
        "control": "[privacy] Offer a quiet-feedback option before speaking a sensitive label.",
        "residual_risk": "A user could still choose spoken feedback in a shared space.",
    },
    "Changed timer duration": {
        "asset": "Integrity of the duration used for a fictional spoken timer.",
        "threat": "[integrity] The requested timer duration is altered before the timer starts.",
        "control": "[integrity] Validate the duration and ask for confirmation before starting.",
        "residual_risk": "A user could confirm the wrong duration or misunderstand the prompt.",
    },
}


def _topic_tags(description):
    """Find author-supplied tags; this is not semantic/security analysis."""
    lower = description.lower()
    return {topic for topic in TOPIC_TAGS if "[{}]".format(topic) in lower}


def check_scenario(scenario):
    """Return PASS/FAIL/REVIEW based on four fields and shared topic tags.

    FAIL: a required field is absent, empty, or not a nonempty string.
    REVIEW: fields exist, but the threat/control topic tags do not overlap.
    PASS: fields exist and those author-supplied tags overlap.

    PASS means only that structure is complete and tags agree; it does NOT
    prove the descriptions are accurate, relevant, safe, or effective.
    """
    if not isinstance(scenario, dict):
        return {"status": "FAIL", "reason": "scenario must be a dictionary"}

    missing = [
        field for field in REQUIRED_FIELDS
        if not isinstance(scenario.get(field), str) or not scenario[field].strip()
    ]
    if missing:
        return {"status": "FAIL", "reason": "missing or blank fields: " + ", ".join(missing)}

    shared = _topic_tags(scenario["threat"]) & _topic_tags(scenario["control"])
    if not shared:
        return {
            "status": "REVIEW",
            "reason": "threat/control topic tags do not overlap; human review needed",
        }

    return {
        "status": "PASS",
        "reason": "four fields present; shared topic tag(s): " + ", ".join(sorted(shared)),
    }


def main():
    print("FICTIONAL spoken-timer scenarios — STRUCTURE ONLY (not correctness)")
    for name, scenario in SCENARIOS.items():
        result = check_scenario(scenario)
        print("{}: {} — {}".format(name, result["status"], result["reason"]))


if __name__ == "__main__":
    main()
