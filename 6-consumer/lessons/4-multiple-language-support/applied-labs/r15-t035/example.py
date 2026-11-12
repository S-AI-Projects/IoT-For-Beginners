"""Security-scenario rubric checker (R15-T035).

Standard library only. A SIMULATION on fictional scenarios: no translator
service, key, model or device is used. The checker verifies STRUCTURE only.
A human must judge whether an explanation is actually good.

A scenario is a dict with the fields: asset, threat, control, residual_risk.

Rubric (status):
  fail   - a required field is missing, empty or not a string
  review - all fields present, but the control does not address the named
           threat (or the threat is not one the rubric knows): a human decides
  pass   - all fields present and the control matches the threat

Two versions with the same contract:
  check_scenario_baseline  - everything inline in one function
  check_scenario           - the "does the control match the threat" step is
                             extracted into control_addresses_threat()
"""

FIELDS = ("asset", "threat", "control", "residual_risk")

# threat keyword -> words that a control addressing it should contain
THREAT_CONTROLS = {
    "key exposure": ("key vault", "rotate", "environment variable", "secret store"),
    "data in transit": ("https", "tls", "encrypt"),
    "mistranslation": ("human review", "back-translation", "confirm", "fallback"),
}


# ---- baseline: one function does everything ---------------------------------
def check_scenario_baseline(scenario):
    problems = []
    for f in FIELDS:
        v = scenario.get(f) if isinstance(scenario, dict) else None
        if not isinstance(v, str) or not v.strip():
            problems.append("missing " + f)
    if problems:
        return {"status": "fail", "problems": problems}

    threat = scenario["threat"].lower()
    control = scenario["control"].lower()
    matched = False
    known = False
    for key, words in THREAT_CONTROLS.items():
        if key in threat:
            known = True
            for w in words:
                if w in control:
                    matched = True
    if known and matched:
        return {"status": "pass", "problems": []}
    return {"status": "review",
            "problems": ["control does not address the named threat"]}


# ---- refactor: one named responsibility extracted ---------------------------
def missing_fields(scenario):
    out = []
    for f in FIELDS:
        v = scenario.get(f) if isinstance(scenario, dict) else None
        if not isinstance(v, str) or not v.strip():
            out.append("missing " + f)
    return out


def control_addresses_threat(threat, control):
    """The extracted responsibility: True only if the threat is a known kind
    and the control contains a word that addresses that kind."""
    threat, control = threat.lower(), control.lower()
    for key, words in THREAT_CONTROLS.items():
        if key in threat and any(w in control for w in words):
            return True
    return False


def check_scenario(scenario):
    problems = missing_fields(scenario)
    if problems:
        return {"status": "fail", "problems": problems}
    if control_addresses_threat(scenario["threat"], scenario["control"]):
        return {"status": "pass", "problems": []}
    return {"status": "review",
            "problems": ["control does not address the named threat"]}


# ---- fictional fixture, tied to sections of the lesson ----------------------
SCENARIOS = [
    {   # section: Create a translator resource
        "name": "translator key in source code",
        "asset": "Translator resource API key",
        "threat": "key exposure: key committed to a public repository",
        "control": "Keep the key in an environment variable and rotate it if leaked",
        "residual_risk": "A key already copied before rotation could still be misused",
    },
    {   # section: Translate text using an AI service
        "name": "user text sent for translation",
        "asset": "",   # missing on purpose
        "threat": "data in transit: text read on the network",
        "control": "Send requests over HTTPS",
        "residual_risk": "The service provider still receives the text",
    },
    {   # section: Translate text
        "name": "wrong control for the threat",
        "asset": "Translated safety announcement",
        "threat": "mistranslation of a safety message",
        "control": "Use a longer API key",
        "residual_risk": "A wrong translation could still be shown",
    },
]


if __name__ == "__main__":
    for s in SCENARIOS:
        print(s["name"], "->", check_scenario(s))
