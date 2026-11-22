"""
Capability Negotiation — Invariant and State Trace (R15-T014)

Lesson reference: 4-manufacturing/lessons/4-trigger-fruit-detector/README.md
Concept: Edge sensors trigger manufacturing detectors (such as fruit quality classification)
over standard IoT protocols. Prior to dispatching work, client and server negotiate
supported capabilities by calculating the intersection of declared capability sets.
Any attempt to invoke an unnegotiated capability must be rejected before dispatch.

Focus:
Record intermediate state after each step (handshake, negotiation, pre-dispatch validation, dispatch)
and enforce the invariant linking negotiated state to final dispatch output.
"""

from typing import Any, Dict, List, Optional, Set, Tuple


class NegotiationSession:
    """
    Manages capability negotiation and records intermediate execution traces.
    """

    def __init__(self, client_capabilities: Set[str], server_capabilities: Set[str]):
        self.client_capabilities = set(client_capabilities)
        self.server_capabilities = set(server_capabilities)
        self.negotiated_capabilities: Optional[Set[str]] = None
        self.state_trace: List[Dict[str, Any]] = []
        self._record_state("INIT", {
            "client_caps": sorted(list(self.client_capabilities)),
            "server_caps": sorted(list(self.server_capabilities)),
        })

    def _record_state(self, step: str, details: Dict[str, Any]):
        entry = {
            "step": step,
            "details": details,
        }
        self.state_trace.append(entry)

    def negotiate(self) -> Set[str]:
        """Calculates set intersection of client and server capabilities."""
        self.negotiated_capabilities = self.client_capabilities.intersection(self.server_capabilities)
        self._record_state("NEGOTIATE", {
            "negotiated_caps": sorted(list(self.negotiated_capabilities)),
        })
        return self.negotiated_capabilities

    def dispatch(self, capability: str, payload: Any = None) -> Tuple[bool, str]:
        """
        Attempts to dispatch a call to a capability.
        Rejects immediately if the capability was not negotiated.
        """
        if self.negotiated_capabilities is None:
            self._record_state("DISPATCH_FAILURE", {
                "capability": capability,
                "reason": "Negotiation has not taken place",
            })
            return False, "REJECTED: Negotiation has not taken place"

        # Pre-dispatch check
        if capability not in self.negotiated_capabilities:
            self._record_state("DISPATCH_REJECTED", {
                "capability": capability,
                "reason": f"Capability '{capability}' was not negotiated",
                "active_negotiated": sorted(list(self.negotiated_capabilities)),
            })
            return False, f"REJECTED: Capability '{capability}' was not negotiated"

        # Successful dispatch
        self._record_state("DISPATCH_SUCCESS", {
            "capability": capability,
            "payload": payload,
        })
        return True, f"SUCCESS: Capability '{capability}' dispatched successfully"

    def verify_invariant(self, capability: str, dispatch_result: bool) -> bool:
        """
        Invariant check:
        dispatch_result is True IF AND ONLY IF capability was in the negotiated set.
        """
        was_negotiated = (
            self.negotiated_capabilities is not None
            and capability in self.negotiated_capabilities
        )
        return dispatch_result == was_negotiated


def run_demo():
    client_caps = {"tools", "resources"}
    server_caps = {"tools", "prompts"}

    session = NegotiationSession(client_caps, server_caps)
    negotiated = session.negotiate()
    print("Negotiated capabilities:", negotiated)

    # Calling resources should be rejected before dispatch
    res_status, res_msg = session.dispatch("resources")
    print(f"Calling 'resources': status={res_status}, msg={res_msg}")

    # Calling tools should succeed
    tools_status, tools_msg = session.dispatch("tools", payload={"action": "detect_fruit"})
    print(f"Calling 'tools': status={tools_status}, msg={tools_msg}")

    print("State trace:")
    for entry in session.state_trace:
        print(" ", entry)

    return session
