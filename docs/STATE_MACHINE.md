# STATE_MACHINE.md

## Purpose

This document defines the deterministic safety state machine used by the **AMNION-ORACLE** reference controller.

Goals:
- enforce safe bounds by design
- make transitions auditable
- keep behavior reproducible under identical inputs

---

## Initial state

**Initial state:** `OK`

---

## Priority of transition conditions

Multiple triggers can occur in the same tick. The controller MUST apply this priority order:

1. **LOCK** (hard stop) always wins
2. Escalation to a stricter state (e.g., `WARN → THROTTLE`)
3. Lateral transitions (rare; if defined)
4. De-escalation to a less strict state (e.g., `THROTTLE → WARN`)

If multiple reasons apply within the same priority level, the controller MUST:
- select the strictest resulting state deterministically
- log **all** triggering reasons (not just the first one)

---

## State set

| State     | Meaning                | Allowed actions |
|----------|------------------------|-----------------|
| OK       | Nominal operation      | normal tick execution |
| WARN     | Approaching limits     | warn-only, increased logging |
| THROTTLE | Controlled reduction   | reduce duty cycle / reduce intensity |
| ISOLATE  | Subsystem separation   | disable non-essential channels |
| DEGRADED | Minimal safe mode      | minimal tick, strict constraints |
| LOCK     | Hard stop              | stop outputs, require manual unlock |

---

## Common terms

- **tick:** one controller cycle (**Model → Act → Sense → Adjust**)
- **metrics:** measured or derived values that drive transitions (read-only inputs)
- **thresholds:** limits loaded from config (`configs/*.yaml`)
- **hysteresis:** different enter/exit thresholds to prevent oscillation
- **dwell:** minimum time (ticks) to stay in state before exiting

---

## Metrics (reference set)

This repo may implement more metrics, but these are recommended as a minimum:

- `q_factor` (dimensionless): effective quality / stability measure
- `damping` (dimensionless): effective damping estimate
- `phase_noise` (rad): Δφ estimate
- `temp_c` (°C): temperature
- `power_w` (W): power draw estimate
- `fault_count` (int): accumulated fault signals
- `sensor_health` (0..1): sensor confidence / validity

**Rule:** Metrics are **read-only** inputs to the state machine.  
The state machine MUST NOT mutate metrics; it only reads them and emits decisions.

---

## Transition rules (high level)

Transitions depend on threshold crossings + fault conditions + optional dwell/hysteresis.

### OK → WARN

Enter `WARN` if any early warning threshold is exceeded, e.g.:
- `q_factor < q_warn_min`
- `phase_noise > phi_warn_max`
- `temp_c > temp_warn_max`
- `sensor_health < sensor_warn_min`

Exit `WARN` back to `OK` only if metrics return within safe band (with hysteresis), e.g.:
- `q_factor >= q_ok_min`
- `phase_noise <= phi_ok_max`
- `temp_c <= temp_ok_max`
- `sensor_health >= sensor_ok_min`

---

### WARN → THROTTLE

Enter `THROTTLE` if degradation continues or hard warning thresholds are crossed:
- `q_factor < q_throttle_min`
- `phase_noise > phi_throttle_max`
- repeated `WARN` for `warn_dwell_ticks` without recovery

Exit `THROTTLE` to `WARN` (or `OK`) only when stable for `throttle_dwell_ticks`.

---

### THROTTLE → ISOLATE

Enter `ISOLATE` if:
- sensor failures persist
- faults exceed `fault_isolate_count`
- instability persists beyond `throttle_timeout_ticks`

Exit `ISOLATE` only after:
- sensor validation passes
- fault reset conditions are met (policy defined in config)
- stability holds for `isolate_recover_ticks`

---

### ISOLATE → DEGRADED

Enter `DEGRADED` if:
- partial subsystem recovery fails repeatedly
- repeated isolate cycles exceed `isolate_cycle_limit`
- safety requires long-duration minimal-mode persistence

**Meaning of DEGRADED:**  
`DEGRADED` is a **long-term minimal safe persistence mode**. The system runs only the minimal controller tick required to remain safe and observable, with strict constraints and reduced functionality.

Exit `DEGRADED` only when:
- all critical metrics are healthy for `degraded_recover_ticks`
- AND a recovery condition is satisfied (configurable):
  - explicit operator action (manual recovery), OR
  - explicit simulation-only auto-recovery flag, OR
  - verified stable window with strict checks

---

### Any state → LOCK (hard stop)

Enter `LOCK` immediately on any hard-stop condition:

- `temp_c >= temp_lock_max`
- `power_w >= power_lock_max`
- critical sensor invalidation
- integrity failure / config invalid
- repeated faults beyond `fault_lock_count`

`LOCK` is terminal until explicit unlock:
- manual unlock mechanism (out of scope for docs)
- or controlled reset in simulation environment (if enabled)

---

## Recommended hysteresis + dwell

Hysteresis prevents chatter:
- entering a stricter state uses tighter thresholds than leaving it

Dwell prevents rapid oscillation:
- minimum ticks in each state before transitioning down

---

## Logging requirements (per tick)

Every tick MUST log:

- timestamp
- `tick_id`
- `state_before → state_after`
- triggering metric(s) (all reasons if multiple)
- thresholds used
- decision summary (action/no-op)
- faults and sensor health snapshot
- `controller_version`
- `config_hash` (or equivalent config integrity digest)

Example log fields:

- `state=THROTTLE`
- `reason=phase_noise_high`
- `phase_noise=0.84`
- `phi_throttle_max=0.70`
- `action=duty_cycle_reduce`
- `controller_version=0.1.0`
- `config_hash=sha256:...`

---

## Testing expectations

At minimum:

- deterministic replay: same inputs → same log sequence
- threshold boundary tests: exact crossings trigger correct transitions
- hysteresis tests: no oscillation under jitter
- lock tests: hard thresholds force `LOCK`
- priority tests: simultaneous triggers always resolve using the defined priority order

See `docs/09_TEST_PROTOCOLS.md` for procedures.
