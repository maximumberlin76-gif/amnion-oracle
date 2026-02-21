04_STABILITY_METRICS.md (Draft)

This document defines mathematical criteria for evaluating dynamic stability (coherence) of the AMNION-ORACLE system.


1) Fundamental State Variables

Canonical parameters:

G     — control gain
K     — coupling coefficient
D     — damping coefficient
P_max — maximum allowed power

1.1) Resonance Model Interface

The coherence model defined in docs/specs/resonance_model.md
provides the state-vector and derived metrics used in this section.

Inputs from resonance layer:

    r_order
    state_vector
    phase_mean
    coherence_score

These values are treated as physical observables.
04_STABILITY_METRICS does not define resonance physics —
it only defines stability evaluation rules applied to them.

For each subsystem `i`, the following parameters are computed:

Qᵢ (Quality Factor) — dimensionless measure of subsystem coherence and resonance retention (0..1).


- P_mismatch — power imbalance:  
  P_mismatch = P_draw − P_in
- φ_error — phase error relative to system mean phase:  
  φ_error = |φᵢ − φ_avg|

 
2) Loss Function and Q Degradation

System quality factor is dynamic and decreases when mismatch grows.

φ_error is provided by resonance_model phase statistics.

Total Loss (L)

\[
L = \alpha \cdot (P_{mismatch})^2 + \beta \cdot \sin^2(\phi_{error})
\]

where:

- α — sensitivity to power mismatch,
- β — sensitivity to phase mismatch.

Q Update Rule (Smooth Exponential Decay)

If Q falls below Q_crit, Guard layer must trigger Barrier mode (see 03_SAFETY_LOGIC.md).

To avoid discontinuous behavior (“saw-tooth instability”), Q is updated via exponential smoothing:

\[
Q_{t+1} = \max(Q_{min},\ Q_t \cdot e^{-\delta \cdot L})
\]

where:

- δ — sensitivity coefficient (penalizes non-resonant / unstable behavior),
- Q_min — minimum allowed Q floor.


3) Soft Power Throttle (No Hard Cutoff)

Hard cutoffs create instability. Instead, use a soft saturation coefficient S:

\[
S = 1.0 - \left(\frac{P_{draw}}{P_{max}}\right)^2
\]

As `P_draw → P_max`, system gain is smoothly reduced:

[ G_{i(active)} = G_i \cdot S ]


This prevents control oscillations and maintains continuity of regulation.


4) Barrier Triggers (Protective Isolation Protocol)

The system monitors Q in real time and activates defensive modes.

States:

Coherent:
    Q > 0.8
    Nominal mode, full synchronization

Warning:
    0.5 < Q ≤ 0.8
    Enable Soft Throttle, notify node

Critical (Barrier):
    Q ≤ Q_crit
    Decouple + Damp + Cap

4.1) ABRAXAS-764 Core Metrics Mapping

- AZ (Master Oscillator)  -> metrics.f_ref
- RCY (Vector ALU)        -> metrics.intent_vector
- SLOVO (Storage/Matrix) -> metrics.state_integrity
- VOZVRAT (Phase Reset)  -> metrics.phase_error
- Z-Loop (Plasma Loop)   -> metrics.loop_closure


4.2) Additional Stability Metrics

metrics.f_ref            — reference resonance frequency
metrics.intent_vector    — normalized intention / computation vector
metrics.state_integrity  — storage coherence [0..1]
metrics.loop_closure     — boolean (true if Z-loop closed)


4.3) ABRAXAS Stability Invariants

I6 — Resonance lock  
|metrics.f_ref − 76.4| ≤ f_tol

I7 — Loop closure  
metrics.loop_closure == TRUE

I8 — State integrity  
metrics.state_integrity ≥ integrity_min


4.4) Escalation Rule

Violation of any of I6, I7, or I8 → enter S2_BARRIER

5) Engineering Conclusion

Stability over time is achieved not by external enforcement, but by internal energetic cost of mismatch.

Non-resonant behavior (parasitic power draw or phase deviation) becomes energetically unfavorable, forcing automatic degradation of Q and finally subsystem isolation via the Barrier protocol.

This converts “ethics-as-stability” into a strictly physical control law:
mismatch → loss → Q decay → isolation.

No policy layer is allowed to override this chain.
