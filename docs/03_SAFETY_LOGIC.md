03_SAFETY_LOGIC — AMNION-ORACLE

Project: AMNION-ORACLE  
Type: Safety / guard logic specification  
Status: Documentation-first (no clinical use)

0. Non-medical / non-clinical disclaimer
 
Safety loop position in system:

Sense → Analyze → Estimate → Guard → Policy → Actuate

Guard is evaluated BEFORE any control action.
If Guard rejects state, system must NOT call Policy().  

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

gain        -> G
coupling    -> K
damping     -> D
power limit -> P_max

2. Core safety invariants

I1 — Power constraint
Never exceed power budget:
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
cap power (P_max ↓)
    

S2 — Barrier mode (decouple + damp + cap)
Triggered when:
- mismatch severe
- risk of runaway oscillation
- sensor failure / instability

Actions:
- `γ → 0` (decouple)
- `ζ → high` (strong damping)
- `P_budget → minimum`
- freeze fast adaptation loops

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

> Barrier = decouple + damp + cap

- decouple: `γ → 0`
- damp: `ζ ↑`
- cap: `P_budget ↓`


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


8. Logging schema (minimal)

Each control decision logs:
- `ts`
- `state`
- `P_draw, P_in, mismatch_power`
- `φ, φ_avg, mismatch_phase`
- `Q, coherence`
- `action_codes[]`
- `hash(snapshot)`


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
