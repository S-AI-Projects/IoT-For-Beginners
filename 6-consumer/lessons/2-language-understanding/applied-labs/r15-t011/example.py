"""
Explicit Access-Policy Evaluation (R15-T011)

Lesson reference: 6-consumer/lessons/2-language-understanding/README.md
Concept: Language understanding services extract intents (actions) and entities (resources)
from spoken phrases. An IoT system must evaluate explicit authorization policies against the
caller's identity/role before dispatching commands.

Security model:
1. Default Deny: If no allow rule matches, access is DENIED.
2. Deny Overrides: Any explicit matching DENY rule overrides any matching ALLOW rule.
3. Unknown Role: Any role not recognized in the policy matrix is DENIED.
"""

from typing import Dict, List, NamedTuple, Optional, Tuple


class PolicyRule(NamedTuple):
    effect: str  # "ALLOW" or "DENY"
    role: str
    action: str
    resource: str


DEFAULT_POLICY_MATRIX: List[PolicyRule] = [
    # reader role
    PolicyRule("ALLOW", "reader", "read", "public"),
    PolicyRule("DENY", "reader", "write", "*"),
    PolicyRule("DENY", "reader", "read", "restricted"),

    # editor role
    PolicyRule("ALLOW", "editor", "read", "*"),
    PolicyRule("ALLOW", "editor", "write", "public"),
    PolicyRule("DENY", "editor", "write", "restricted"),  # explicit deny overrides allow

    # admin role
    PolicyRule("ALLOW", "admin", "*", "*"),
    PolicyRule("DENY", "admin", "delete", "system-root"),  # explicit deny overrides wildcard allow
]

KNOWN_ROLES = {"reader", "editor", "admin"}


def match_field(rule_val: str, req_val: str) -> bool:
    """Checks whether a rule field matches the request field (* matches everything)."""
    return rule_val == "*" or rule_val.lower() == req_val.lower()


def evaluate_access(
    role: str,
    action: str,
    resource: str,
    policies: Optional[List[PolicyRule]] = None,
    known_roles: Optional[set] = None,
) -> Tuple[bool, str]:
    """
    Evaluates whether (role, action, resource) is permitted.
    Returns: (is_allowed: bool, reason: str)
    
    Rules:
    - Unknown role -> False (Deny)
    - If any matching DENY rule exists -> False (Deny overrides Allow)
    - Else if any matching ALLOW rule exists -> True (Allow)
    - Otherwise -> False (Default Deny)
    """
    policies = policies if policies is not None else DEFAULT_POLICY_MATRIX
    roles = known_roles if known_roles is not None else KNOWN_ROLES

    # Rule 1: Unknown role check
    if role not in roles:
        return False, f"DENY: Role '{role}' is unknown"

    matched_allows = []
    matched_denies = []

    for rule in policies:
        if (
            match_field(rule.role, role)
            and match_field(rule.action, action)
            and match_field(rule.resource, resource)
        ):
            if rule.effect == "DENY":
                matched_denies.append(rule)
            elif rule.effect == "ALLOW":
                matched_allows.append(rule)

    # Rule 2: Explicit deny overrides allow
    if matched_denies:
        return False, f"DENY: Explicit deny rule matched ({matched_denies[0]})"

    # Rule 3: Allow if at least one matching allow exists
    if matched_allows:
        return True, f"ALLOW: Matched allow rule ({matched_allows[0]})"

    # Rule 4: Default deny
    return False, "DENY: Default deny (no allow rule matched)"


def run_demo() -> Dict[str, Tuple[bool, str]]:
    """Runs standard evaluation scenarios."""
    scenarios = {
        "reader_read_public": ("reader", "read", "public"),
        "reader_write_public": ("reader", "write", "public"),
        "editor_write_restricted": ("editor", "write", "restricted"),
        "unknown_role_read": ("guest", "read", "public"),
    }
    results = {}
    for name, (r, a, res) in scenarios.items():
        allowed, reason = evaluate_access(r, a, res)
        results[name] = (allowed, reason)
        print(f"[{'ALLOW' if allowed else 'DENY'}] {name}: role={r}, action={a}, resource={res} -> {reason}")
    return results


if __name__ == "__main__":
    run_demo()
