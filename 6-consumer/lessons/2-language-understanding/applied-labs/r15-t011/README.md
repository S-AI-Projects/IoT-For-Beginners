# Applied Lab: Explicit Access-Policy Evaluation (R15-T011)

This lab extends the [Language Understanding lesson](../../README.md) by demonstrating how an IoT consumer device or backend service validates access control once an intent (action) and entity (resource) are extracted from user speech.

## Concept & Curriculum Connection

In smart assistants (e.g., smart timers or home controllers), natural language processing extracts an **intent** (e.g. `read`, `write`, `set_timer`) and target **entities** (e.g. `public`, `timer_duration`, `system_settings`). Before dispatching actions to IoT actuators or data stores, the system must evaluate an explicit authorization matrix against the caller's identity or role.

### Security Contract
1. **Default Deny:** Any action or resource not explicitly permitted by a rule is denied.
2. **Deny Overrides Allow:** If any matching rule has an effect of `DENY`, the request is denied regardless of any matching `ALLOW` rules.
3. **Role Validation:** Unknown or unauthenticated roles are immediately denied.

## Local Fixture & Test Matrix

The local example evaluates decisions using the following deterministic policy matrix:
- `reader`:
  - `ALLOW read public`
  - `DENY write *`
  - `DENY read restricted`
- `editor`:
  - `ALLOW read *`
  - `ALLOW write public`
  - `DENY write restricted` (explicit deny overriding allow)
- `admin`:
  - `ALLOW * *`
  - `DENY delete system-root` (explicit deny overriding allow)

### Expected Outputs
- `("reader", "read", "public")` -> `ALLOW`
- `("reader", "write", "public")` -> `DENY`
- `("editor", "write", "restricted")` -> `DENY` (Deny overrides Allow)
- `("guest", "read", "public")` -> `DENY` (Unknown role)

## Running the Code & Automated Tests

Prerequisites: Python 3 standard library (no external packages or cloud accounts required).

### Run Example
```bash
python3 6-consumer/lessons/2-language-understanding/applied-labs/r15-t011/example.py
```

### Run Tests
```bash
python3 -m unittest discover -s 6-consumer/lessons/2-language-understanding/applied-labs/r15-t011 -p "test_*.py"
```

## Simulation Scope & Limitations
- **Local Fixture:** This implementation evaluates in-memory authorization rules without connecting to external cloud services (such as Azure LUIS or Entra ID).
- **Hardware Boundary:** No physical microphone, speaker, or IoT development board is required; all inputs and outputs operate through pure Python contracts.
