# Applied Lab: Capability Negotiation — Invariant and State Trace (R15-T014)

This lab extends the [Trigger Fruit Quality Detection from a Sensor lesson](../../README.md) by implementing protocol-level capability negotiation between IoT sensor clients and manufacturing classification servers.

## Concept & Curriculum Connection

When a hardware trigger (such as an optical proximity or break-beam sensor) detects fruit on an assembly line, it initiates a connection to a downstream processing node or vision service. Distributed IoT systems require both endpoints to negotiate supported capabilities (e.g. tools, prompts, resources) prior to executing commands.

### Protocol Contract
1. **Capability Intersection:** The active set of capabilities is defined as $C_{\text{negotiated}} = C_{\text{client}} \cap C_{\text{server}}$.
2. **Pre-Dispatch Guard:** Invocation of any capability not present in $C_{\text{negotiated}}$ is rejected before dispatch.
3. **State Trace & Invariant:** Every lifecycle transition (initialization, negotiation, dispatch rejection, dispatch success) is recorded in an intermediate state trace. The invariant guarantees:
   $$\text{dispatch}(c) = \text{SUCCESS} \iff c \in C_{\text{negotiated}}$$

## Fixture & Scenarios
- Client capabilities: `{"tools", "resources"}`
- Server capabilities: `{"tools", "prompts"}`
- Negotiated output: `{"tools"}`
- Invocation of `"resources"`: Rejected before dispatch (`REJECTED: Capability 'resources' was not negotiated`).
- Invocation of `"tools"`: Permitted and dispatched (`SUCCESS`).

## Verification & Execution

Prerequisites: Python 3 standard library.

### Run Example
```bash
python3 4-manufacturing/lessons/4-trigger-fruit-detector/applied-labs/r15-t014/example.py
```

### Run Tests
```bash
python3 -m unittest discover -s 4-manufacturing/lessons/4-trigger-fruit-detector/applied-labs/r15-t014 -p "test_*.py"
```

## Simulation Scope & Limitations
- **In-Memory Negotiation:** Simulates capability handshakes without network sockets, MQTT brokers, or TLS certificates.
- **Hardware Boundary:** No physical factory conveyor, proximity sensor, or camera hardware is required.
