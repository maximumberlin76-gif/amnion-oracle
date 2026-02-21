# RUNTIME_INTEGRATION — SCM / Law-X Bridge (Concept)

Purpose

Document optional external runtime integration.
AMNION-ORACLE MUST remain standalone.
Law-X is an optional external guard/runtime that can provide advisory risk signals and forensic logging.

Design rule:
- Controller is authoritative for safety invariants and state transitions.
- Law-X provides advisory recommendations and anomaly classification.
- No external runtime can bypass docs/STATE_MACHINE.md priority (LOCK > escalation > lateral > de-escalation).

---

## Runtime Artifact

Reference runtime module (external):
- lawx_full_stack.py
  - Hardened FastAPI (API key + HMAC + anti-replay + forensic hash-chain in SQLite)
  - L1 detector: AntiArtificialDissipation (patterns: WIDEBAND_NOISE, SLOW_POISON, SELECTIVE_DESTRUCTION, PROXY_GROWTH_GAP)
  - L0 executor: HeartGuardL0 (fast per-frame guard, split strikes physics vs phase)
  - Engine: SingularConscienceEngine (L1 pre-check + thawing, no 1-step lag)

This repository does not embed deployment instructions beyond concept-level integration notes.

---

## Integration Boundary

Controller runs locally in deterministic mode.

Law-X MAY provide:
- advisory mode: ALLOW / THROTTLE / ISOLATE / DEGRADE
- pattern label + confidence
- forensic signature (attack_signature) and stable log chain

Law-X MUST NOT provide:
- direct actuation commands
- overrides for ethics invariants
- state machine transition authority

---

## Controller ↔ Law-X Contract

### Input (to Law-X)

A single tick/frame payload MUST contain only read-only metrics:

- phase_noise
- q_factor (or proxy)
- power_w (or power_noise proxy)
- temp_c
- sensor_health
- fault_count
- optional: reported_growth, energy_input (for PROXY_GROWTH_GAP detection)

Rule:
Controller MUST NOT send personal data, medical claims, or user identity fields.

### Output (from Law-X)

Law-X returns an advisory object:

- lawx_mode: ALLOW | THROTTLE | ISOLATE | DEGRADE
- lawx_pattern: string (e.g., WIDEBAND_NOISE)
- lawx_confidence: float [0..1]
- attack_signature: short stable hash (for forensic correlation)

---

## Mapping into AMNION State Machine

Law-X is advisory. Mapping is conservative:

- lawx_mode = ALLOW
  -> no change

- lawx_mode = THROTTLE
  -> controller MAY escalate up to WARN/THROTTLE depending on thresholds

- lawx_mode = ISOLATE
  -> controller MAY escalate to ISOLATE if not already stricter

- lawx_mode = DEGRADE
  -> controller MAY escalate to DEGRADED
  -> controller MAY escalate to LOCK if any hard-stop invariant is violated

Hard rule:
If any hard-stop condition of docs/STATE_MACHINE.md is true, controller MUST enter LOCK regardless of Law-X output.

---

## Deterministic Replay Rule

External runtime MUST NOT affect deterministic replay.

Replay mode behavior:
- runtime calls are disabled OR replaced with recorded Law-X responses
- identical inputs + identical config -> identical logs and transitions

No time-based or network jitter is allowed to influence decisions in replay mode.

---

## Failure Policy

If Law-X is unavailable or returns invalid output:
- controller assumes lawx_mode = ALLOW
- controller logs runtime_fault flag
- controller continues using internal thresholds and invariants only

If Law-X returns malformed/untrusted response:
- ignore response
- log integrity_fault
- do not de-escalate as a result of runtime data

---

## Security Boundary (Concept)

If Law-X API is used:
- API key required
- HMAC signing required (RAW or CANONICAL JSON)
- anti-replay nonce + time window
- forensic hash-chain stored in SQLite (cross-worker safe)

Security rule:
Security features protect the runtime endpoint.
They do not change controller safety invariants.

End of file.
