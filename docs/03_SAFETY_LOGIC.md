03_SAFETY_LOGIC — AMNION-ORACLE
Project: AMNION-ORACLE
Type: Safety / guard logic specification
Status: Documentation-first (no clinical use)

0) Non-medical / non-clinical disclaimer

AMNION-ORACLE is a concept-level engineering reference.
It is NOT a medical device and NOT intended for clinical use.

Safety loop position in system
sense -> preprocess -> estimate -> metrics -> guard -> control -> actuate -> log

Guard is evaluated BEFORE any control action.
If Guard rejects state, system must NOT call control().

1) Safety goal

The system must remain stable, predictable, and non-destructive under:
- power mismatch
- phase mismatch / drift
- noisy input signals
- missing sensors / invalid data
- external disturbances
- operator errors

Primary invariant: Do no harm (system + operator + environment).

2) Parameter naming (canonical)

gain -> G  
coupling -> K  
damping -> D  
power limit -> P_max  
power budget -> P_budget  
power budget min -> P_budget_min  
power budget soft -> P_budget_soft  

3) Guard evaluation order (canonical)

1. Sensor validity check  
2. Power budget check  
3. Phase mismatch check  
4. Coherence / Q check  
5. Rate-of-change check  
6. State transition decision  
7. Output patching (clamp / throttle / decouple / damp / cap)

No step may be skipped.
If any step fails, Guard escalates state before control output is computed.

4) Core safety invariants

I1 — Power constraint  
0 <= P_draw <= P_max  
Soft saturation only. No hard cutoff.

I2 — Coherence constraint  
Coherence is never forced to perfect.  
Coherence is stabilized by damping + decoupling.

I3 — Phase stability  
Phase correction is gradual.  
No aggressive phase kicks.

I4 — Conservative behavior on uncertainty  
If sensors invalid or contradictory:  
- reduce coupling  
- reduce gain  
- cap power  
- switch to safe mode  

I5 — Deterministic logging  
Every critical decision logs:
- timestamp
- reason codes
- measurement snapshot
- hashes where relevant

5) Guard escalation priority (highest first)

1. Sensor invalid / missing  
2. Power overflow  
3. Coherence collapse  
4. Phase runaway  
5. Rate-of-change violation  

Higher priority always overrides lower.

6) Guard states

S0_NORMAL  
S1_THROTTLE  
S2_BARRIER  
S3_SAFE_HALT  

Transitions:

S0 -> S1 : threshold exceeded  
S1 -> S2 : severe mismatch OR sensor failure  
S2 -> S3 : repeated violation OR coherence < C_floor  
S2 -> S1 : parameters stabilized  
S1 -> S0 : all metrics within envelope  
S3 -> S0 : manual restart only  

7) Barrier definition (canonical)

Barrier = decouple + damp + cap

decouple: K -> 0  
damp: D -> high  
cap: P_budget -> minimum  

Barrier is not a phase flip.

8) Anti-oscillation rule

Hard cutoff creates oscillation (saw behavior).

Therefore:
- use saturator (clamp)
- adaptive throttle near limits
- smooth transitions

Recommended:
P_draw = clamp(P_draw, 0, P_max)
reduce alpha as P_draw -> P_max

9) Safe parameter floors

Q = max(Q_min, Q + dQ)
Q must never go negative.
No runaway compensations.

10) Sensor sanity checks

Before control update:
- range checks
- derivative checks
- plausibility across sensors
- missing value handling

If invalid -> enter S1 or S2 depending on severity.

11) Guard function (canonical)

function guard(state, metrics, config):

    P_max = config.P_max
    P_budget_min = config.P_budget_min
    P_budget_soft = config.P_budget_soft

    Q_crit = config.Q_crit
    phase_trip = config.phase_trip
    rate_trip = config.rate_trip
    rate_limit = config.rate_limit

    PATCH_NONE = none

    PATCH_BARRIER =
        set_K(0),
        set_D_high(),
        set_P_budget(P_budget_min),
        freeze_fast_adaptation()

    PATCH_THROTTLE =
        reduce_G(),
        reduce_K(),
        increase_D(),
        set_P_budget(P_budget_soft)

    if sensors_invalid(metrics):
        return S2_BARRIER, PATCH_BARRIER

    if metrics.P_draw > P_max:
        return S2_BARRIER, PATCH_BARRIER

    if metrics.Q <= Q_crit:
        return S2_BARRIER, PATCH_BARRIER

    if abs(metrics.phase_error) > phase_trip:
        return S2_BARRIER, PATCH_BARRIER

    if abs(metrics.rate_change) > rate_trip:
        return S2_BARRIER, PATCH_BARRIER

    if abs(metrics.rate_change) > rate_limit:
        return S1_THROTTLE, PATCH_THROTTLE

    if within_envelope(metrics, config):
        return S0_NORMAL, PATCH_NONE

    return S1_THROTTLE, PATCH_THROTTLE

12) Design principle

Safety logic is monotonic:
the system may always become more conservative,
but never more aggressive after a violation.

AMNION-ORACLE remains documentation-first and non-clinical.
