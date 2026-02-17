# STATE_MACHINE

## Purpose
This document defines the **deterministic safety state machine** used by the AMNION-ORACLE reference controller.

Goals:
- enforce safe bounds by design
- make transitions auditable
- keep behavior reproducible under identical inputs

## State set
| State      | Meaning | Allowed actions |
|------------|---------|-----------------|
| OK         | Nominal operation | normal tick execution |
| WARN       | Approaching limits | warn-only, increased logging |
| THROTTLE   | Controlled reduction | reduce duty cycle / reduce intensity |
| ISOLATE    | Subsystem separation | disable non-essential channels |
| DEGRADED   | Minimal safe mode | minimal tick, strict constraints |
| LOCK       | Hard stop | stop outputs, require manual unlock |

## Common terms
- **tick**: one controller cycle (Model → Act → Sense → Adjust)
- **metrics**: measured or derived values that drive transitions
- **thresholds**: limits loaded from config (`configs/*.yaml`)
- **hysteresis**: different enter/exit thresholds to prevent oscillation
- **dwell**: minimum time (ticks) to stay in state before exiting

## Metrics (reference set)
This repo may implement more metrics, but these are recommended as a minimum:

- `q_factor` (dimensionless): effective quality / stability measure
- `damping` (dimensionless): effective damping estimate
- `phase_noise` (rad): Δφ estimate
- `temp_c` (°C): temperature
- `power_w` (W): power draw estimate
- `fault_count` (int): accumulated fault signals
- `sensor_health` (0..1): sensor confidence / validity

## Transition rules (high level)
Transitions depend on **threshold crossings** + **fault conditions** + optional dwell/hysteresis.

### OK → WARN
Enter WARN if any early warning threshold is exceeded, e.g.:
- `q_factor < q_warn_min`
- `phase_noise > phi_warn_max`
- `temp_c > temp_warn_max`
- `sensor_health < sensor_warn_min`

Exit WARN back to OK only if metrics return within safe band:
- `q_factor >= q_ok_min` (with hysteresis)
- `phase_noise <= phi_ok_max`
- `temp_c <= temp_ok_max`
- `sensor_health >= sensor_ok_min`

### WARN → THROTTLE
Enter THROTTLE if degradation continues or hard warning thresholds are crossed:
- `q_factor < q_throttle_min`
- `phase_noise > phi_throttle_max`
- repeated WARN for `warn_dwell_ticks` without recovery

Exit THROTTLE to WARN (or OK) when stable for `throttle_dwell_ticks`.

### THROTTLE → ISOLATE
Enter ISOLATE if:
- sensor failures persist
- faults exceed `fault_isolate_count`
- instability persists beyond `throttle_timeout_ticks`

Exit ISOLATE only after:
- sensor validation passes
- faults reset conditions are met
- stability holds for `isolate_recover_ticks`

### ISOLATE → DEGRADED
Enter DEGRADED if:
- partial subsystem recovery fails
- repeated isolate cycles exceed `isolate_cycle_limit`
- safety requires minimal-mode persistence

Exit DEGRADED only when:
- all critical metrics are healthy
- manual or explicit recovery condition is satisfied (configurable)

### Any state → LOCK (hard stop)
Enter LOCK immediately on:
- `temp_c >= temp_lock_max`
- `power_w >= power_lock_max`
- critical sensor invalidation
- integrity failure / config invalid
- repeated faults beyond `fault_lock_count`

LOCK is terminal until explicit unlock:
- manual unlock mechanism (out of scope for docs)
- or controlled reset in simulation environment

## Recommended hysteresis + dwell
Hysteresis prevents chatter:
- entering a stricter state uses tighter threshold than leaving it

Dwell prevents rapid oscillation:
- minimum ticks in each state before transitioning down

## Logging requirements (per tick)
Every tick MUST log:
- timestamp
- tick_id
- state_before → state_after
- triggering metric(s)
- thresholds used
- decision summary (action/no-op)
- faults and sensor health snapshot

Example log fields:
- `state=THROTTLE`
- `reason=phase_noise_high`
- `phase_noise=0.84`
- `phi_throttle_max=0.70`
- `action=duty_cycle_reduce`

## Testing expectations
At minimum:
- deterministic replay: same inputs → same log sequence
- threshold boundary tests: exact crossings trigger correct transitions
- hysteresis tests: no oscillation under jitter
- lock tests: hard thresholds force LOCK

See `docs/09_TEST_PROTOCOLS.md` for procedures.
