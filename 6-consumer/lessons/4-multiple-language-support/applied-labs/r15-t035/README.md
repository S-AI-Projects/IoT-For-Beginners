# R15-T035: security-scenario rubric, refactoring the teaching example

Extends the [Support multiple languages](../../README.md) lesson. The lesson
sends text and a key to a translator service; this example describes three
fictional security scenarios and checks that each answer is complete.

**Scope:** a local simulation in standard-library Python 3 on fictional
scenarios. No translator service, key, model or device. The checker verifies
**structure only**: it cannot judge whether an explanation is good, so a human
must review the reasoning. The keyword matching is a deliberate simplification.

## Scenario fields

`asset`, `threat`, `control`, `residual_risk`. All four must be non-empty text.

## Rubric

| Status | When |
|---|---|
| pass | all four fields present and the control addresses the named threat |
| fail | any field missing, empty or not text (for example no asset) |
| review | fields present, but the control does not address the named threat, or the threat is not a known kind; a human decides |

Known threats and control words: *key exposure* (key vault, rotate,
environment variable, secret store), *data in transit* (https, tls, encrypt),
*mistranslation* (human review, back-translation, confirm, fallback).

## Fixture and expected output

| Scenario | Lesson section | Result |
|---|---|---|
| translator key in source code | Create a translator resource | pass |
| user text sent for translation (asset missing) | Translate text using an AI service | fail, `missing asset` |
| wrong control for the threat (longer API key vs mistranslation) | Translate text | review |

## Refactor: baseline then extract one responsibility

`check_scenario_baseline` does everything in one function. `check_scenario`
has the same contract, with the step "does this control address this threat"
extracted into `control_addresses_threat`, and field checking into
`missing_fields`. The tests prove both return identical results on the fixture
and on many variations.

## Run

```
python3 6-consumer/lessons/4-multiple-language-support/applied-labs/r15-t035/example.py
python3 -m unittest discover -s 6-consumer/lessons/4-multiple-language-support/applied-labs/r15-t035 -p "test_*.py"
```
