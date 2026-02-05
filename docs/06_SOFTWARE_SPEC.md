06_SOFTWARE_SPEC — AMNION-ORACLE (Software Specification)

Project: AMNION-ORACLE  
Type: Software specification (documentation-first)  
Scope: Control loop + safety layer + logging + simulation  
Status: Concept / reference implementation notes (NOT clinical)

0. Non-medical / non-clinical disclaimer
AMNION-ORACLE is a concept-level engineering reference.
It is **NOT** a medical device and **NOT** intended for clinical use.


1. Goals
- Deterministic, reproducible controller behavior
- Strict guard separation: control vs safety/safeguards
- Text-based configuration and stable interfaces
- Full audit: logs + hashes
  
Monotonic safety behavior (system may become more conservative, never more aggressive after violation)

2. Runtime modes
3. M1 — Simulator-only
- Synthetic sensors
- Recorded traces
- Deterministic replay

M2 — Host-control loop (Python/Node)
- Reads sensors (or data feed)
- Computes control output
- Writes actuator commands (stub or hardware adapter)

M3 — Embedded loop (MCU)
- Optional future path
- Same logic, reduced compute


3. Module boundaries (clean interfaces)
- `core/` — control loop + internal state
- `safety/` — guard rules, barrier behavior, interlocks
- `io/` — sensor adapters + actuator adapters (pluggable)
- `sim/` — simulation harness + replay runner
- `log/` — event log + snapshot hash + manifest



4. Configuration format
All configs are text-based (YAML/JSON).
Must support:
- controller gains
- thresholds (power, phase mismatch, noise floor)
- time constants (τ, damping, throttling curves)
- guard states and transitions
- output caps / budgets

Example keys (concept-level):
- `P_max`, `P_budget`
- `Q_min`, `Q_max`
- `phase_drift_max`
- `sensor_timeout_ms`
- `barrier_timeout_ms`


5. Data model (minimal)
Inputs:
- `P_in`, `P_draw`
- `phi` (phase), `phi_avg`
- `Q` (quality / coherence proxy)
- `noise_sigma`
- `sensor_valid[]`

Derived:
- `mismatch_power = P_draw - P_in`
- `mismatch_phase = |phi - phi_avg|`
- `coherence_score` (0..1)

Outputs:
- `u_control` (control action)
- `u_throttle` (soft limiter)
- `guard_state`


6. Logging / audit
Must record:
- timestamp
- mode (sim/host/mcu)
- inputs + derived metrics
- outputs
- guard transitions
- barrier entries/exits
- snapshot hash (SHA-256)

Log formats:
- `events.jsonl` (append-only)
- `snapshots/` (optional)
- `manifest.txt` with hashes


7. Error handling policy
- Invalid sensor → degrade mode
- Missing sensor → fallback estimate + strict caps
- Unstable metrics → barrier mode
- Any ambiguous state → safe clamp + damp


8. Minimal reference implementation plan
- Step 1: Simulator harness
- Step 2: Safety logic verified in sim
- Step 3: Interface stubs for hardware IO
- Step 4: Deterministic replay tests
  
