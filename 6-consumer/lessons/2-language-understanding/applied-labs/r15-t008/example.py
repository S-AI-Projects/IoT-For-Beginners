"""Explicit access-policy evaluation — failure and recovery example (R15-T008).

Standard library only. A SIMULATION: does not call LUIS, Azure Cognitive Services,
or smart speaker audio hardware.

Focus:
  Evaluates allow/deny authorization for intent requests recognized by language
  understanding systems.
  Exercises documented invalid/missing-data error scenarios and demonstrates
  graceful fault isolation and immediate recovery on the next valid request.

Rules:
  1. Default deny.
  2. Deny overrides allow.
  3. Reader may read public resources but cannot write.
  4. Explicit deny overrides matching allow.
  5. Unknown role is denied.
  6. Invalid or missing input returns deny with error description without crashing.
"""

KNOWN_ROLES = {"reader", "editor", "admin"}

# (role, action, resource, effect)
POLICY_RULES = [
    ("reader", "read", "public", "allow"),
    ("editor", "read", "*", "allow"),
    ("editor", "write", "*", "allow"),
    ("editor", "write", "locked", "deny"),  # explicit deny overrides allow
    ("admin", "*", "*", "allow"),
]


def _match_pattern(rule_val: str, query_val: str) -> bool:
    return rule_val == "*" or rule_val.lower() == query_val.lower()


class AccessPolicyEvaluator:
    """Stateful policy engine demonstrating failure containment and recovery."""

    def __init__(self, policy=POLICY_RULES, known_roles=KNOWN_ROLES):
        self.policy = policy
        self.known_roles = known_roles
        self.error_count = 0
        self.processed_count = 0

    def evaluate(self, role, action, resource) -> tuple:
        """Evaluates an access request. Returns (decision, reason).

        Gracefully catches invalid/missing input, increments error count,
        and safely returns ('deny', reason) allowing immediate recovery.
        """
        self.processed_count += 1

        # Check for missing/invalid data types
        if not all(isinstance(v, str) for v in (role, action, resource)):
            self.error_count += 1
            return "deny", "Invalid input: role, action, and resource must all be non-null strings"

        role_clean = role.strip().lower()
        action_clean = action.strip().lower()
        res_clean = resource.strip().lower()

        if not role_clean or not action_clean or not res_clean:
            self.error_count += 1
            return "deny", "Invalid input: role, action, and resource cannot be empty strings"

        if role_clean not in self.known_roles:
            return "deny", f"Unknown role: '{role}' is not a recognized role"

        matched_allow = False
        for r, a, res, effect in self.policy:
            if _match_pattern(r, role_clean) and _match_pattern(a, action_clean) and _match_pattern(res, res_clean):
                if effect == "deny":
                    return "deny", "Explicit deny rule overrides allow"
                matched_allow = True

        if matched_allow:
            return "allow", "Matched allow policy rule"

        return "deny", "Default deny: no matching allow rule found"


if __name__ == "__main__":
    evaluator = AccessPolicyEvaluator()
    print("1. Valid reader:", evaluator.evaluate("reader", "read", "public"))
    print("2. Reader write:", evaluator.evaluate("reader", "write", "public"))
    print("3. Missing data (Failure):", evaluator.evaluate("reader", "", "public"))
    print("4. Recovery (Valid next):", evaluator.evaluate("reader", "read", "public"))
