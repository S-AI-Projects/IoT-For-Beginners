"""Local access-policy evaluator (R15-T031).

Standard library only. A SIMULATION: it does not call LUIS, Azure or any
hardware. It only illustrates how an app might decide whether a recognised
intent (an "action") by a role on a resource is allowed.

Rules:
  1. Default deny.
  2. Deny overrides allow.
  3. A reader may read public resources but cannot write.
  4. An unknown role is denied.
"""

ROLES = {"reader", "editor", "admin"}

# (role, action, resource) -> effect. "*" matches any action/resource.
POLICY = [
    ("reader", "read", "public", "allow"),
    ("editor", "read", "*", "allow"),
    ("editor", "write", "*", "allow"),
    ("editor", "write", "locked", "deny"),   # deny beats the allow above
    ("admin", "*", "*", "allow"),
]


def _matches(rule_value, value):
    return rule_value == "*" or rule_value == value


def evaluate(role, action, resource, policy=POLICY):
    """Return (decision, reason). decision is 'allow' or 'deny'."""
    if not all(isinstance(v, str) and v for v in (role, action, resource)):
        return "deny", "invalid input (empty or non-string)"
    if role not in ROLES:
        return "deny", "unknown role"
    allowed = False
    for r, a, res, effect in policy:
        if r == role and _matches(a, action) and _matches(res, resource):
            if effect == "deny":
                return "deny", "explicit deny"
            allowed = True
    if allowed:
        return "allow", "matched allow rule"
    return "deny", "default deny"


if __name__ == "__main__":
    for case in [("reader", "read", "public"), ("reader", "write", "public"),
                 ("editor", "write", "locked"), ("guest", "read", "public"),
                 ("", "read", "public")]:
        print(case, "->", *evaluate(*case))
