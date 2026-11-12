# R15-T031: explicit access-policy evaluation

A small local example that extends the [Understand language](../../README.md) lesson.
After LUIS recognises an intent (for example "set a timer"), an app still has to
decide whether the caller is *allowed* to do it. This example evaluates a
role / action / resource matrix.

**Scope:** simulated, standard-library Python 3 only. No LUIS, Azure, models,
GPUs or hardware are used, and nothing here claims to match how a real cloud
service enforces policy.

## Run

```
python3 6-consumer/lessons/2-language-understanding/applied-labs/r15-t031/example.py
python3 -m unittest discover -s 6-consumer/lessons/2-language-understanding/applied-labs/r15-t031 -p "test_*.py"
```

## Rules

1. Default deny. 2. Deny overrides allow. 3. A reader may read public resources but cannot write. 4. An unknown role is denied.

## Cases

| Kind | Input (role, action, resource) | Output | Why |
|---|---|---|---|
| Smallest valid | reader, read, public | allow | matches the one allow rule |
| Boundary | reader, write, public | deny (default deny) | read is allowed, write has no rule |
| Boundary | reader, read, private | deny (default deny) | only *public* is allowed |
| Boundary | editor, write, locked | deny (explicit deny) | deny beats the broader allow |
| Invalid | guest, read, public | deny (unknown role) | role not in the known set |
| Invalid | "", read, public | deny (invalid input) | empty value |

## Where the simplification stops

Real systems also have identity (authentication), groups, inheritance, resource
hierarchies and audit logs. This example has a flat role list and exact or `*` matching only.
