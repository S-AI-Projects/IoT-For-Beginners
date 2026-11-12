"""Minimal launch-configuration check (R15-T040).

Standard library only. A SIMULATION: the configuration is only CHECKED and
summarised. The process is never launched (this module does not import
subprocess), and no Azure Functions, IoT Hub, model or device is involved.

A configuration is a dict:
  command : non-empty string, the program to start         (lesson: `func`)
  args    : a LIST of strings, never one string            (lesson: ["start"])
  env     : dict of explicitly named keys -> string values (lesson: the
            settings in local.settings.json, e.g. IOT_HUB_CONNECTION_STRING)

validate(cfg) returns a report:
  {"ok": bool, "errors": [str], "summary": dict or None}
Every environment VALUE is redacted in the summary; only the key names show.
"""

import json
import re
import sys

REDACTED = "<redacted>"
ENV_KEY = re.compile(r"^[A-Z_][A-Z0-9_]*$")

# Each public input/output and the lesson idea it stands for.
LESSON_CONCEPTS = {
    "command": "the program that starts the app, as in `func start`",
    "args": "separate arguments, as in `func start` where `start` is its own item; "
            "a list keeps argument boundaries exact",
    "env": "named settings your app reads, as in the Values section of local.settings.json",
    "summary.env": "connection strings contain a secret key, so values are never shown",
    "summary.launched": "this example checks the configuration only; `func start` is never run",
    "errors": "what to fix before running the app",
}


def validate(cfg):
    """Check a configuration. Never launches anything."""
    errors = []
    if not isinstance(cfg, dict):
        return {"ok": False, "errors": ["configuration must be a dict"], "summary": None}

    command = cfg.get("command")
    if not isinstance(command, str) or not command.strip():
        errors.append("command is missing or empty")

    args = cfg.get("args", [])
    if isinstance(args, str):
        errors.append("args must be a list of strings, not a single string")
    elif not isinstance(args, list) or not all(isinstance(a, str) for a in args):
        errors.append("args must be a list of strings")

    env = cfg.get("env", {})
    if not isinstance(env, dict):
        errors.append("env must be a dict of NAME -> value")
    else:
        for key, value in env.items():
            if not isinstance(key, str) or not ENV_KEY.match(key):
                errors.append("env key %r is not a valid NAME" % (key,))
            elif not isinstance(value, str):
                errors.append("env value for %s must be a string" % key)

    if errors:
        return {"ok": False, "errors": errors, "summary": None}
    return {
        "ok": True,
        "errors": [],
        "summary": {
            "command": command,
            "args": list(args),
            "env": {k: REDACTED for k in env},
            "launched": False,
        },
    }


def main(argv=None):
    """Read a JSON configuration file, print the report. Exit code 0 if valid, 1 if not."""
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) != 1:
        print("usage: example.py CONFIG.json")
        return 2
    try:
        with open(argv[0], encoding="utf-8") as f:
            cfg = json.load(f)
    except (OSError, ValueError) as err:
        print("cannot read configuration: %s" % err)
        return 2
    report = validate(cfg)
    print(json.dumps(report, indent=2))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    DEMO = {"command": "func", "args": ["start"],
            "env": {"IOT_HUB_CONNECTION_STRING": "HostName=demo;SharedAccessKey=not-a-real-key"}}
    for label, cfg in [("valid", DEMO),
                       ("missing command", {"args": ["start"]}),
                       ("args as one string", dict(DEMO, args="start --port 7071"))]:
        print("%s: %s" % (label, json.dumps(validate(cfg))))
