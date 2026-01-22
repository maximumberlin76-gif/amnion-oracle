04_STABILITY_METRICS — AMNION-ORACLE

Project: AMNION-ORACLE  
Type: Stability metrics specification  
Status: Documentation-first (no clinical use)  

0. Non-medical / non-clinical disclaimer

AMNION-ORACLE is a concept-level engineering reference.  
It is NOT a medical device and NOT intended for clinical use.


1. Purpose

Define measurable, implementation-agnostic stability metrics for a resonance-based controller architecture.

The metrics must allow:
- verification in simulation
- logging in deterministic form
- comparison between builds / configurations
- safe gating decisions (guards)


2. Core definitions

2.1 Power mismatch (P)

Mismatch power:
- `mismatch_power = P_draw - P_in`

Where:
- `P_draw` = power demanded by system / actuator / load
- `P_in`   = power available from source / budget / supply

Interpretation:
- `mismatch_power > 0` = deficit (danger)
- `mismatch_power < 0` = surplus (can charge / damp)


2.2 Phase mismatch (φ)

Phase mismatch measures deviation from expected coherence.

Options (choose one as canonical per implementation):
- `mismatch_phase = abs(φ - φ_avg)`
- or normalized:
  - `mismatch_phase = sin(φ - φ_avg)`

Where:
- `φ` = current phase estimate
- `φ_avg` = reference / running average / target


2.3 Coherence metric (C)

Coherence is the stability indicator of internal synchronization.

Canonical range:
- `C ∈ [0, 1]`

Interpretation:
- `C ≈ 1` → coherent / stable
- `C → 0` → decoupled / unstable

Minimal operational threshold:
- `C_min ≈ 0.73` (recommended)


2.4 Q-factor (Q)

Q-factor represents the retention / stability capacity of the system.

Rule:
- Q must never “run negative” or diverge.

Safe update forms:

Option A (bounded additive):
- `current_Q = max(Q_min, current_Q + delta_Q)`

Option B (exponential decay under loss):
- `current_Q = max(Q_min, current_Q * exp(-δ * loss))`

Where:
- `Q_min` is a hard floor



3. Stability score (S)

Provide a single scalar “stability score” for logging and guard logic.

Example form:

- `S = wC*C - wP*norm(mismatch_power) - wφ*norm(mismatch_phase) - wN*noise_level`

Where:
- `wC, wP, wφ, wN` are weights
- `norm(x)` maps to `[0..1]`

Interpretation:
- higher `S` means safer / more stable state


4. Guard thresholds

Recommended threshold set (initial defaults):
- `C_min = 0.73`
- `P_max_deficit = P_budget * 0.15`
- `φ_max = φ_limit`
- `Q_min = Q_floor`

Guard decision sample:
- if `C < C_min` → enter guard state
- if `mismatch_power > P_max_deficit` → throttle + damp
- if `mismatch_phase > φ_max` → decouple + damp


5. Cutoff policy: avoid hard cutoffs

Hard cutoff often produces oscillation (“saw pattern”) near limits.

Recommended:
- `saturator + throttle`
- reduce gains smoothly near `P_max`

Example:
- `P_draw = clamp(P_draw, 0..P_max)`
- decrease controller gain `α_i` as `P_draw → P_max`


6. Barrier state (canonical interpretation)

Barrier is NOT just a phase flip.

Engineering meaning:
- decouple + damp + cap

Actions:
- reduce coupling: `γ_i → 0`
- increase damping: `ζ ↑`
- enforce power budget: `P_budget`


7. Logging (deterministic)

Each cycle must log:

- timestamp / tick
- `P_draw, P_in, mismatch_power`
- `φ, φ_avg, mismatch_phase`
- `C`
- `Q`
- guard_state
- stability_score `S`
- config_hash

Logs must support:
- reproducibility
- hashing
- integrity verification


8. Output format suggestion

Minimal JSON line format per tick:

- one line = one tick
- deterministic key order
- stable float rounding

Example keys:
- `t, P_draw, P_in, dP, phi, phi_ref, dphi, C, Q, S, guard, cfg`


9. Notes

This document describes a measurement layer only.
Implementation may be MCU firmware + host controller (Python/Node)
or fully embedded control loop.
