03_SAFETY_LOGIC — AMNION-ORACLE

Project: AMNION-ORACLE  
Type: Safety / guard logic specification  
Status: Documentation-first (no clinical use)

0. Non-medical / non-clinical disclaimer
 
Safety loop position in system:

sense → preprocess → estimate → metrics → guard → control → actuate → log

Guard is evaluated BEFORE any control action. If Guard rejects state, system must NOT call control().

AMNION-ORACLE is a concept-level engineering reference.  
It is NOT a medical device and NOT intended for clinical use.


1. Safety goal

The system must remain stable, predictable, and non-destructive under:
- power mismatch
- phase mismatch / drift
- noisy input signals
- missing sensors / invalid data
- external disturbances
- operator errors

Primary invariant: Do no harm (system + operator + environment).

Parameter naming (canonical):

    gain -> G
    coupling -> K
    damping -> D
    power limit -> P_max
    power budget -> P_budget
    power budget min -> P_budget_min
    power budget soft -> P_budget_soft

Guard evaluation order (canonical)

Guard processes inputs in strict sequence:

1. Sensor validity check
2. Power budget check
3. Phase mismatch check
4. Coherence / Q check
5. Rate-of-change check
6. State transition decision
7. Output patching (clamp / throttle / decouple / damp / cap)

No step may be skipped.
If any step fails, Guard escalates state before control output is computed.

2. Core safety invariants

I1 — Power constraint Never exceed power limit:
- `0 ≤ P_draw ≤ P_max`
- enforce soft saturation (not hard cutoff)

I2 — Coherence constraint
Maintain temporal coherence:
- coherence is never forced to “perfect”
- coherence is stabilized by damping + decoupling

I3 — Phase stability
Phase mismatch must not cause oscillatory runaway:
- phase correction is gradual
- avoid aggressive phase “kicks”

I4 — Conservative behavior on uncertainty
If sensors are invalid or contradictory:
- reduce coupling
- reduce gain
- cap power
- switch to safe mode

I5 — Deterministic logging
Every critical decision must be reproducible:
- timestamp
- reason codes
- measurement snapshot
- hashes where relevant

Guard escalation priority (highest first):

1. Sensor invalid / missing
2. Power overflow
3. Coherence collapse
4. Phase runaway
5. Rate-of-change violation

Higher priority conditions always override lower ones.

3. Guard states

State transitions:

S0 -> S1 : threshold exceeded
S1 -> S2 : severe mismatch OR sensor failure
S2 -> S3 : repeated violation OR coherence < C_floor
S2 -> S1 : parameters stabilized
S1 -> S0 : all metrics within envelope
S3 -> S0 : manual restart only 

S1 — Warning / throttle
Triggered when:
- mismatch exceeds threshold
- coherence falls below target


 Actions:
    reduce gain (G ↓)
    reduce coupling (K ↓)
    increase damping (D ↑)
    cap power budget (P_budget ↓)   

S2 — Barrier mode (decouple + damp + cap)
Triggered when:
- mismatch severe
- risk of runaway oscillation
- sensor failure / instability

Actions:

    K → 0 (decouple)
    D → high (strong damping)
    P_budget → minimum
    freeze fast adaptation loops

S3 — Safe halt / lock
Triggered when:
- repeated instability
- multiple sensor failures
- coherence collapse below floor

Actions:
- stop active control output
- keep logging + minimal monitoring
- require manual restart

4. Barrier definition (canonical)

Barrier ≠ phase flip (metaphor only).  
Engineering definition:

Barrier = decouple + damp + cap

    decouple: K → 0
    damp: D ↑
    cap: P_budget ↓


5. Anti-oscillation rule

Hard cutoff creates oscillation (“saw behavior”).  
Therefore:
- use saturator (`clamp`)
- adaptive throttle near limits
- smooth transitions

Recommended:
- `P_draw = clamp(P_draw, 0, P_max)`
- reduce `α` as `P_draw → P_max`


6. Safe parameter floors

Never allow unstable negatives:
- `Q = max(Q_min, Q + ΔQ)`
- avoid `Q < 0`
- avoid runaway compensations


7. Sensor sanity checks

Before control update:
- range checks
- derivative checks (jumps)
- plausibility checks across sensors
- missing value handling

If invalid:
- enter S1/S2 depending on severity

8.8. Guard function (canonical)

# Canonical function: guard()
# Inputs : state, metrics, config
# Outputs: (guard_state, patch)

function guard(state, metrics, config):

    # ===== Aliases (canonical names) =====
    P_max          = config.P_max
    P_budget_min   = config.P_budget_min
    P_budget_soft  = config.P_budget_soft

    Q_crit     = config.Q_crit
    phase_trip = config.phase_trip
    rate_trip  = config.rate_trip
    rate_limit = config.rate_limit

    # ===== Patch definitions =====
    PATCH_NONE = patch(none)

    # Barrier = decouple + damp + cap (hard)
    PATCH_BARRIER = patch(
        set_K(0),                 # decouple
        set_D_high(),             # strong damping
        set_P_budget(P_budget_min),
        freeze_fast_adaptation()
    )

    # Throttle = conservative soft limitation
    PATCH_THROTTLE = patch(
        reduce_G(),
        reduce_K(),
        increase_D(),
        set_P_budget(P_budget_soft)
    )

    # ===== 1) Sensor validity (highest priority) =====
    if sensors_invalid(metrics):
        return S2_BARRIER, PATCH_BARRIER

    # ===== 2) Power overflow =====
    if metrics.P_draw > P_max:
        return S2_BARRIER, PATCH_BARRIER

    # ===== 3) Coherence / Q collapse =====
    if metrics.Q <= Q_crit:
        return S2_BARRIER, PATCH_BARRIER

    # ===== 4) Phase runaway =====
    if abs(metrics.phase_error) > phase_trip:
        return S2_BARRIER, PATCH_BARRIER

    # ===== 5) Rate-of-change (two-tier) =====
    if abs(metrics.rate_change) > rate_trip:
        return S2_BARRIER, PATCH_BARRIER

    if abs(metrics.rate_change) > rate_limit:
        return S1_THROTTLE, PATCH_THROTTLE

    # ===== 6) Normal envelope =====
    if within_envelope(metrics, config):
        return S0_NORMAL, PATCH_NONE

    # ===== 7) Default conservative =====
    return S1_THROTTLE, PATCH_THROTTLE

9. Summary

This safety logic provides:
- stability-first behavior
- clear safety states
- formal barrier mode
- deterministic reasoning trace

Design principle:

Safety logic is monotonic:
system may always become more conservative,
but never more aggressive after a violation.

AMNION-ORACLE remains documentation-first and non-clinical
