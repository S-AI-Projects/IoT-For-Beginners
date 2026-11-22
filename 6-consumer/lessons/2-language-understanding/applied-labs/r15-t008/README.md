# R15-T008: Explicit Access-Policy Evaluation — Failure & Recovery Example

An applied laboratory extension for the [Understand language](../../README.md) lesson.

## Educational Context & Scope

When a voice assistant parses spoken language into an intent (action) and entity parameters (resources), the backend application must decide whether the invoking user (role) is authorized to perform that action on that resource.

This lab implements a deterministic authorization matrix evaluating:
1. **Default Deny:** If no allow rule explicitly matches, the request is denied.
2. **Deny Overriding Allow:** Specific negative security policies (e.g. `editor` writing to `locked` assets) override broader wildcards.
3. **Role Enforcement:** Unrecognized roles are denied.
4. **Failure Containment & Immediate Recovery:** Malformed, missing, or null payload parameters are safely handled without throwing uncaught exceptions, ensuring the service remains healthy and immediately handles subsequent valid utterances.

**Scope:** Python 3 standard library simulation. No LUIS, Azure Cognitive Services, microphones, or smart speakers required.

## Run

```bash
python3 6-consumer/lessons/2-language-understanding/applied-labs/r15-t008/example.py
python3 -m unittest discover -s 6-consumer/lessons/2-language-understanding/applied-labs/r15-t008 -p "test_*.py"
```

## Policy Decision Matrix

| Role | Action | Resource | Decision | Reason / Rule |
|---|---|---|---|---|
| `reader` | `read` | `public` | `allow` | Matches explicit allow rule |
| `reader` | `write` | `public` | `deny` | Default deny (readers cannot write) |
| `editor` | `write` | `notes` | `allow` | Matches editor write wildcard `*` |
| `editor` | `write` | `locked` | `deny` | Explicit deny overrides general allow |
| `guest` | `read` | `public` | `deny` | Unknown role rejected |
| `reader` | `""` | `public` | `deny` (error) | Documented failure: empty action string |
| `reader` | `read` | `public` | `allow` | **Immediate Recovery:** subsequent valid input succeeds |

## Where the Simplification Stops

Production identity management (e.g. OAuth 2.0 / OpenID Connect, Azure RBAC, AWS IAM) evaluates hierarchical attribute-based access control (ABAC), token expiration, revocation lists, distributed tenant boundaries, and immutable audit logs.
