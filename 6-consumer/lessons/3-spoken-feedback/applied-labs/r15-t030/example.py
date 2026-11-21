#!/usr/bin/env python3
"""Security-Scenario Rubric — Scenario Assessment.

Coursework Task: R15-T030
Context Lesson: 6-consumer/lessons/3-spoken-feedback

This module implements a deterministic rubric checker for IoT spoken feedback security scenarios.
It assesses structured scenarios covering voice impersonation, timer endpoint manipulation,
and SSML injection.

Rubric Outcomes:
  - PASS: All required fields populated; control contains relevant keywords for the threat.
  - FAIL: A required field (asset, threat, control, residual_risk) is missing or blank.
  - REVIEW: All fields populated, but control lacks relevant keywords addressing the threat.

Educational Scope & Limitations:
  This is a local, rule-based keyword heuristic for educational assessment.
  It does NOT perform natural language understanding, nor does it guarantee or prove
  real-world control effectiveness on physical IoT devices, Azure Speech services, or ML models.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import sys
from typing import Any, Dict, List, Optional, Tuple


REQUIRED_FIELDS = ("asset", "threat", "control", "residual_risk")

# Threat-to-control keyword rules specific to Lesson 6-3 concepts
THREAT_RUBRIC_RULES: Dict[str, Dict[str, List[str]]] = {
    "voice_impersonation": {
        "threat_keywords": [
            "voice",
            "impersonation",
            "replay",
            "synthesized",
            "synthetic",
            "cloned",
            "audio recording",
        ],
        "control_keywords": [
            "voice-only",
            "separate",
            "authenticated confirmation",
            "multi-factor",
            "confirmation",
            "secondary",
            "out-of-band",
            "companion device",
        ],
    },
    "ssml_manipulation": {
        "threat_keywords": [
            "ssml",
            "markup",
            "injection",
            "altering speech",
            "untrusted markup",
            "speech synthesis",
        ],
        "control_keywords": [
            "escaping",
            "escape",
            "allow-list",
            "allowlist",
            "sanitize",
            "sanitization",
            "approved ssml",
        ],
    },
    "timer_request": {
        "threat_keywords": [
            "rest",
            "timer",
            "duration",
            "endpoint",
            "timer request",
        ],
        "control_keywords": [
            "authentication",
            "token",
            "validation",
            "bounds",
            "hmac",
            "https",
            "mutual",
            "server-side",
        ],
    },
}


@dataclass
class EvaluationVerdict:
    """The outcome of assessing a security scenario against the rubric."""

    status: str  # "PASS", "FAIL", or "REVIEW"
    reason: str
    matched_threat_domain: Optional[str] = None
    missing_field: Optional[str] = None


def assess_security_scenario(scenario: Dict[str, Any]) -> EvaluationVerdict:
    """Assess a security scenario against the deterministic rubric.

    Checks:
      1. All required fields (asset, threat, control, residual_risk) must be present and non-blank.
         Failure results in 'FAIL'.
      2. The threat description is mapped to a known lesson threat domain using keyword matching.
      3. The control description is evaluated for predefined control keywords.
         Match -> 'PASS' (predefined keyword heuristic; does not prove control effectiveness).
         Missing keywords -> 'REVIEW'.
    """
    if not isinstance(scenario, dict):
        return EvaluationVerdict(
            status="FAIL",
            reason=f"Scenario must be a dictionary, got {type(scenario).__name__}.",
            missing_field="schema",
        )

    # 1. Field presence and non-blank check
    for field in REQUIRED_FIELDS:
        if field not in scenario or scenario[field] is None:
            return EvaluationVerdict(
                status="FAIL",
                reason=f"Missing required field: '{field}'.",
                missing_field=field,
            )
        val = scenario[field]
        if not isinstance(val, str) or len(val.strip()) == 0:
            return EvaluationVerdict(
                status="FAIL",
                reason=f"Field '{field}' cannot be empty or whitespace.",
                missing_field=field,
            )

    threat_text = scenario["threat"].lower()
    control_text = scenario["control"].lower()

    # 2. Match threat domain
    matched_domain: Optional[str] = None
    for domain, rule in THREAT_RUBRIC_RULES.items():
        if any(kw in threat_text for kw in rule["threat_keywords"]):
            matched_domain = domain
            break

    if matched_domain is None:
        return EvaluationVerdict(
            status="REVIEW",
            reason="Threat domain unrecognized by rubric rules; requires manual security expert review.",
            matched_threat_domain=None,
        )

    # 3. Check control relevance keywords
    rule = THREAT_RUBRIC_RULES[matched_domain]
    has_relevant_control = any(kw in control_text for kw in rule["control_keywords"])

    if has_relevant_control:
        return EvaluationVerdict(
            status="PASS",
            reason=(
                f"All required fields populated and control matched predefined control "
                f"keywords for '{matched_domain}' (predefined keyword heuristic; does not prove control effectiveness)."
            ),
            matched_threat_domain=matched_domain,
        )
    else:
        return EvaluationVerdict(
            status="REVIEW",
            reason=(
                f"All fields populated, but control lacks relevant predefined keywords addressing '{matched_domain}' "
                f"(requires human reviewer assessment)."
            ),
            matched_threat_domain=matched_domain,
        )


def verify_scenario_expectations(
    scenarios: List[Dict[str, Any]], expected_table: Dict[str, str]
) -> List[Tuple[str, str, str]]:
    """Compare actual scenario assessments against expected outcomes.

    Detects:
      1. A scenario is missing from the expected-results table.
      2. The expected-results table contains an ID for which no scenario was supplied.
      3. An actual verdict differs from its expected verdict.

    Raises:
      AssertionError: If any expectation check fails, identifying the offending scenario ID.

    Returns:
      List of (scenario_id, expected_status, actual_status).
    """
    supplied_ids = {sc.get("id", "UNKNOWN_SCENARIO") for sc in scenarios}

    # 1. Check for scenarios missing from expected_table
    for sc in scenarios:
        sc_id = sc.get("id", "UNKNOWN_SCENARIO")
        if sc_id not in expected_table:
            raise AssertionError(f"Scenario '{sc_id}' is missing from the expected-results table.")

    # 2. Check for unexpected IDs in expected_table for which no scenario was supplied
    extra_ids = set(expected_table.keys()) - supplied_ids
    if extra_ids:
        sorted_extras = sorted(extra_ids)
        raise AssertionError(
            f"Expected-results table contains unexpected scenario ID(s) for which no scenario was supplied: {sorted_extras}"
        )

    # 3. Check for verdict mismatches
    verifications: List[Tuple[str, str, str]] = []
    for sc in scenarios:
        sc_id = sc.get("id", "UNKNOWN_SCENARIO")
        expected_status = expected_table[sc_id]
        verdict = assess_security_scenario(sc)

        if verdict.status != expected_status:
            raise AssertionError(
                f"Outcome mismatch for scenario '{sc_id}': expected '{expected_status}', "
                f"got '{verdict.status}'. Detail: {verdict.reason}"
            )

        verifications.append((sc_id, expected_status, verdict.status))

    return verifications


# --- Standard Fictional Scenarios ---

def get_standard_scenarios() -> Dict[str, Dict[str, Any]]:
    """Return standard fictional scenarios illustrating Lesson 6-3 concepts."""
    return {
        "SCENARIO_1_VOICE": {
            "id": "SCENARIO_1_VOICE",
            "name": "Voice Impersonation & Replay Attack",
            "asset": "Trust in spoken timer feedback and authorized user commands",
            "threat": "Replay attacks or synthetic-voice impersonation of the user using cloned audio",
            "control": "Avoid voice-only authentication and require separate authenticated confirmation on a companion device",
            "residual_risk": "Compromised companion device or social engineering via misleading audio output in shared environments",
        },
        "SCENARIO_2_TIMER": {
            "id": "SCENARIO_2_TIMER",
            "name": "REST Timer Endpoint Manipulation",
            "asset": "Integrity and accuracy of timer duration seconds",
            "threat": "Unauthorized or manipulated REST requests or responses altering duration",
            "control": "Enforce mutual request authentication (HTTPS/tokens) and server-side duration bounds validation",
            "residual_risk": "Compromised API credentials or denial of service against the REST timer endpoint",
        },
        "SCENARIO_3_SSML": {
            "id": "SCENARIO_3_SSML",
            "name": "SSML Markup Injection",
            "asset": "Integrity and safety of spoken audio feedback",
            "threat": "Untrusted markup altering speech output or injecting unauthorized SSML elements",
            "control": "Sanitize input by escaping untrusted text and enforce an allow-list of approved SSML elements",
            "residual_risk": "Syntactically valid but contextually misleading or socially engineered spoken phrasing",
        },
        "SCENARIO_4_MISSING_ASSET": {
            "id": "SCENARIO_4_MISSING_ASSET",
            "name": "Timer Scenario with Missing Asset Field",
            # "asset" field omitted intentionally
            "threat": "Unauthorized or manipulated REST requests or responses",
            "control": "Enforce request authentication and duration bounds validation",
            "residual_risk": "Compromised API credentials",
        },
        "SCENARIO_5_UNRELATED_CONTROL": {
            "id": "SCENARIO_5_UNRELATED_CONTROL",
            "name": "SSML Scenario with Unrelated Physical Control",
            "asset": "Integrity and safety of spoken audio feedback",
            "threat": "Untrusted markup altering speech output",
            "control": "Paint the device casing with water-resistant enamel to protect against moisture",
            "residual_risk": "Scratches on the casing enamel over prolonged usage",
        },
    }


# --- CLI Scenarios ---

def run_normal_scenario() -> None:
    """Run the 3 complete security scenarios and verify expected PASS status."""
    print("=" * 80)
    print("Task R15-T030: Security-Scenario Rubric — Scenario Assessment")
    print("Scenario: normal (Three Complete Lesson Scenarios)")
    print("=" * 80)
    print()

    all_scenarios = get_standard_scenarios()
    scenarios_to_evaluate = [
        all_scenarios["SCENARIO_1_VOICE"],
        all_scenarios["SCENARIO_2_TIMER"],
        all_scenarios["SCENARIO_3_SSML"],
    ]

    expected_table = {
        "SCENARIO_1_VOICE": "PASS",
        "SCENARIO_2_TIMER": "PASS",
        "SCENARIO_3_SSML": "PASS",
    }

    for sc in scenarios_to_evaluate:
        verdict = assess_security_scenario(sc)
        print(f"[{sc['id']}] {sc['name']}")
        print("-" * 80)
        print(f"  Asset:         {sc['asset']}")
        print(f"  Threat:        {sc['threat']}")
        print(f"  Control:       {sc['control']}")
        print(f"  Residual Risk: {sc['residual_risk']}")
        print(f"  Verdict:       {verdict.status}")
        print(f"  Explanation:   {verdict.reason}")
        print()

    # Validate against expected table
    results = verify_scenario_expectations(scenarios_to_evaluate, expected_table)
    print("-" * 80)
    print("VERIFICATION SUMMARY:")
    for sc_id, exp, act in results:
        print(f"  ✓ {sc_id:<28} Expected: {exp:<6} Actual: {act:<6} (MATCH)")
    print("All normal scenarios successfully passed the rubric check.")
    print("=" * 80)


def run_boundary_scenario() -> None:
    """Run boundary cases: missing asset field (FAIL) and unrelated control (REVIEW)."""
    print("=" * 80)
    print("Task R15-T030: Security-Scenario Rubric — Scenario Assessment")
    print("Scenario: boundary (Missing Asset & Unrelated Control Checks)")
    print("=" * 80)
    print()

    all_scenarios = get_standard_scenarios()
    scenarios_to_evaluate = [
        all_scenarios["SCENARIO_4_MISSING_ASSET"],
        all_scenarios["SCENARIO_5_UNRELATED_CONTROL"],
    ]

    expected_table = {
        "SCENARIO_4_MISSING_ASSET": "FAIL",
        "SCENARIO_5_UNRELATED_CONTROL": "REVIEW",
    }

    for sc in scenarios_to_evaluate:
        verdict = assess_security_scenario(sc)
        print(f"[{sc['id']}] {sc['name']}")
        print("-" * 80)
        print(f"  Asset:         {sc.get('asset', '<MISSING>')}")
        print(f"  Threat:        {sc.get('threat', '<MISSING>')}")
        print(f"  Control:       {sc.get('control', '<MISSING>')}")
        print(f"  Residual Risk: {sc.get('residual_risk', '<MISSING>')}")
        print(f"  Verdict:       {verdict.status}")
        print(f"  Explanation:   {verdict.reason}")
        print()

    results = verify_scenario_expectations(scenarios_to_evaluate, expected_table)
    print("-" * 80)
    print("BOUNDARY VERIFICATION SUMMARY:")
    for sc_id, exp, act in results:
        print(f"  ✓ {sc_id:<32} Expected: {exp:<6} Actual: {act:<6} (MATCH)")
    print("All boundary conditions handled cleanly and correctly.")
    print("=" * 80)


def run_failure_scenario() -> None:
    """Execute deliberate wrong expectation assertion to demonstrate non-zero exit."""
    print("=" * 80)
    print("Task R15-T030: Security-Scenario Rubric — Scenario Assessment")
    print("Scenario: failure (Intentional Mismatch Failure Demonstration)")
    print("=" * 80)
    print("Notice: This scenario intentionally asserts an incorrect expected outcome.")
    print("It demonstrates that verification checks properly fail with a non-zero exit code.")
    print("This is an intentional demonstration, not a real security incident.")
    print()

    all_scenarios = get_standard_scenarios()
    target_scenario = [all_scenarios["SCENARIO_1_VOICE"]]

    # Actual outcome for SCENARIO_1_VOICE is PASS, but we deliberately expect FAIL
    corrupted_expected_table = {
        "SCENARIO_1_VOICE": "FAIL",  # Deliberately false expectation
    }

    actual_verdict = assess_security_scenario(target_scenario[0])
    print(f"Target Scenario:            {target_scenario[0]['id']}")
    print(f"Actual Assessed Verdict:    {actual_verdict.status}")
    print(f"Deliberately False Expected: {corrupted_expected_table['SCENARIO_1_VOICE']}")
    print()
    print("Triggering deliberate expectation assertion failure now...")
    print("INTENTIONAL FAILURE: Expected 'FAIL' but actual is 'PASS'.")

    # Deliberately raise AssertionError via verify_scenario_expectations
    verify_scenario_expectations(target_scenario, corrupted_expected_table)


def main() -> None:
    """CLI entrypoint."""
    parser = argparse.ArgumentParser(
        description="Security-Scenario Rubric Assessment (Lesson 6-3 Spoken Feedback)."
    )
    parser.add_argument(
        "--scenario",
        default=None,
        choices=["normal", "boundary", "failure"],
        help="CLI scenario: 'normal', 'boundary', or 'failure'.",
    )
    parser.add_argument(
        "positional_scenario",
        nargs="?",
        default=None,
        choices=["normal", "boundary", "failure"],
        help="Optional positional scenario name.",
    )

    args = parser.parse_args()
    scenario = args.scenario or args.positional_scenario or "normal"

    if scenario == "normal":
        run_normal_scenario()
    elif scenario == "boundary":
        run_boundary_scenario()
    elif scenario == "failure":
        run_failure_scenario()


if __name__ == "__main__":
    main()
