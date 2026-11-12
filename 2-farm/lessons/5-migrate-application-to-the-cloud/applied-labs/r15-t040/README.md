# R15-T040: client-configuration validation, runnable concept example

Extends the [Migrate your application logic to the cloud](../../README.md)
lesson. The lesson starts a local Functions app with `func start`, keeps
secret connection strings in `local.settings.json`, and later uploads them as
application settings. This example checks a launch configuration of that shape
and reports it with secrets redacted.

**Scope:** a local simulation in standard-library Python 3. The configuration
is only **checked and summarised; no process is ever launched**. No Azure
Functions, IoT Hub, model, GPU or device is used, and nothing here describes how
the real tools or cloud services behave. It does not check that the command
exists, that a setting is correct, or that a key is genuine.

## Contract

- `command`: non-empty string. A missing or empty command fails.
- `args`: a **list** of strings. A single string such as `"start --port 7071"` fails.
- `env`: dict of explicitly named keys (upper case, digits, underscore) to string values.
- `validate(config)` returns `{"ok", "errors", "summary"}`. All problems are
  listed together. A valid record gives a summary with every env **value** replaced by `<redacted>`.

## Each input and output, tied to the lesson

| Public name | Lesson concept |
|---|---|
| `command` | the program that starts the app, as in `func start` |
| `args` | separate arguments: in `func start`, `start` is its own item; a list keeps argument boundaries exact |
| `env` | named settings your app reads, as in the Values section of `local.settings.json` |
| `summary.env` | connection strings contain a secret key, so values are never shown |
| `summary.launched` | always `false`: this example checks the configuration only and never runs `func start` |
| `errors` | what to fix before running the app |

The tests check that every public field appears in this table.

## Fixture and expected output

Input: command `func`, args `["start"]`, env `IOT_HUB_CONNECTION_STRING` set to a made-up value.

| Case | Result |
|---|---|
| valid record | `ok` true; summary has `IOT_HUB_CONNECTION_STRING` set to `<redacted>` and `launched` false |
| no command | `ok` false; error `command is missing or empty` |
| args `"start --port 7071"` (one string) | `ok` false; error `args must be a list of strings, not a single string` |

## Run

```
python3 2-farm/lessons/5-migrate-application-to-the-cloud/applied-labs/r15-t040/example.py
python3 -m unittest discover -s 2-farm/lessons/5-migrate-application-to-the-cloud/applied-labs/r15-t040 -p "test_*.py"
```

To check your own file: `python3 .../example.py my-config.json` prints the report
and exits 0 if valid, 1 if not, 2 if the file cannot be read.
