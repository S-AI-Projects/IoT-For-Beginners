# R15-T037: client-configuration validation, evaluation experiment

Extends the [Migrate your application logic to the cloud](../../README.md)
lesson. The lesson starts a local Functions app and keeps connection strings
in settings. This example checks a server-launch configuration (a command, an
argument list and named environment keys) and reports it with secrets redacted.

**Scope:** a local simulation in standard-library Python 3. The configuration
is only **checked and summarised; no process is ever launched**. No Azure
Functions, IoT Hub, model, GPU or device is used, and nothing here says how any
real service behaves. It does not check that the command exists or that
settings are correct for a real deployment.

## Contract

- `command`: non-empty string. A missing or empty command fails.
- `args`: a **list** of strings. A single string such as `"-m server"` fails, because
  argument boundaries must not be guessed by splitting on spaces.
- `env`: dict of explicitly named keys (upper case, digits, underscore) to string values.
- Failures raise `ValueError`.
- A valid record returns a summary with every env **value** replaced by `<redacted>`
  and `launched: False`.

## Evaluation: three controlled sizes

`compare()` validates three configurations that differ only in size. The metric
is the **number of checks made** (deterministic, unlike timing) and the size of
the redacted report in characters, with a check that no secret value appears in the report.

| Config | args | env keys | checks | report chars | secret leaked |
|---|---|---|---|---|---|
| small | 1 | 1 | 4 | 55 | no |
| medium | 10 | 5 | 17 | 190 | no |
| large | 100 | 20 | 122 | 1190 | no |

**Correctness:** all three are valid and none leaks a secret.
**Trade-off observed:** the work grows linearly (checks = 2 + args + env keys),
so a longer argument list costs proportionally more to validate and to report.
The report size does not depend on the *length of a secret*: a test shows the
same report size for secrets of length 1, 8 and 500. This is a count on
synthetic data, not a performance claim about real hardware or cloud services.

## Run

```
python3 2-farm/lessons/5-migrate-application-to-the-cloud/applied-labs/r15-t037/example.py
python3 -m unittest discover -s 2-farm/lessons/5-migrate-application-to-the-cloud/applied-labs/r15-t037 -p "test_*.py"
```
