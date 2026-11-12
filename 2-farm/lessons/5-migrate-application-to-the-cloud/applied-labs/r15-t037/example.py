"""Server-launch configuration validation (R15-T037).

Standard library only. A SIMULATION: the configuration is only CHECKED and
summarised. The process is never launched (this module does not import
subprocess), and no cloud service, model or device is used.

A configuration is a dict with:
  command : non-empty string, the program to run
  args    : a LIST of strings (a single string is rejected, so argument
            boundaries are never guessed by splitting on spaces)
  env     : dict of explicitly named environment keys -> string values.
            Keys must look like NAME or NAME_2 (upper case, digits, underscore).

Invalid configurations raise ValueError. Valid ones return a summary in which
every environment VALUE is redacted.
"""

import re

REDACTED = "<redacted>"
ENV_KEY = re.compile(r"^[A-Z_][A-Z0-9_]*$")


def validate_config(cfg):
    """Return {"ok": True, "checks": n, "summary": {...}} or raise ValueError.

    "checks" counts the individual checks made, a deterministic cost measure.
    """
    checks = 0
    if not isinstance(cfg, dict):
        raise ValueError("configuration must be a dict")

    checks += 1
    command = cfg.get("command")
    if not isinstance(command, str) or not command.strip():
        raise ValueError("command is missing or empty")

    checks += 1
    args = cfg.get("args", [])
    if isinstance(args, str):
        raise ValueError("args must be a list of strings, not a single string")
    if not isinstance(args, list):
        raise ValueError("args must be a list of strings")
    for i, a in enumerate(args):
        checks += 1
        if not isinstance(a, str):
            raise ValueError("args[%d] must be a string" % i)

    env = cfg.get("env", {})
    if not isinstance(env, dict):
        raise ValueError("env must be a dict of NAME -> value")
    for key, value in env.items():
        checks += 1
        if not isinstance(key, str) or not ENV_KEY.match(key):
            raise ValueError("env key %r is not a valid NAME" % (key,))
        if not isinstance(value, str):
            raise ValueError("env value for %s must be a string" % key)

    summary = {
        "command": command,
        "args": list(args),
        "env": {k: REDACTED for k in env},   # keys kept, values never reported
        "launched": False,
    }
    return {"ok": True, "checks": checks, "summary": summary}


def render_summary(summary):
    """One-line text report."""
    return "%s %s | env: %s | launched=%s" % (
        summary["command"], " ".join(summary["args"]),
        ", ".join("%s=%s" % kv for kv in summary["env"].items()) or "(none)",
        summary["launched"])


# Three small controlled configurations, differing in size.
def make_config(n_args, n_env, secret_len=8):
    return {
        "command": "python3",
        "args": ["--opt%d" % i for i in range(n_args)],
        "env": {"KEY_%d" % i: "s" * secret_len for i in range(n_env)},
    }


CONFIGS = {
    "small": make_config(1, 1),
    "medium": make_config(10, 5),
    "large": make_config(100, 20),
}


def compare(configs=CONFIGS):
    """Metric: number of checks made, and size of the redacted report.
    Returns rows of (name, args, env_keys, checks, report_chars, leaked)."""
    rows = []
    for name, cfg in configs.items():
        result = validate_config(cfg)
        text = render_summary(result["summary"])
        leaked = any(v in text for v in cfg["env"].values())
        rows.append((name, len(cfg["args"]), len(cfg["env"]),
                     result["checks"], len(text), leaked))
    return rows


if __name__ == "__main__":
    print("name    args env checks report_chars leaked")
    for row in compare():
        print("%-7s %4d %3d %6d %12d %s" % row)
