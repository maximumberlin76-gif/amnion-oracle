04_STABILITY_METRICS.md (Draft)

This document defines mathematical criteria for evaluating dynamic stability (coherence) of the AMNION-ORACLE system.


1) Fundamental State Variables

Canonical parameters:

G     — control gain
K     — coupling coefficient
D     — damping coefficient
P_max — maximum allowed power


For each subsystem `i`, the following parameters are computed:

Qᵢ (Quality Factor) — dimensionless measure of subsystem coherence and resonance retention (0..1).


- P_mismatch — power imbalance:  
  P_mismatch = P_draw − P_in
- φ_error — phase error relative to system mean phase:  
  φ_error = |φᵢ − φ_avg|


2) Loss Function and Q Degradation

System quality factor is dynamic and decreases when mismatch grows.

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


5) Engineering Conclusion

Stability over time is achieved not by external enforcement, but by internal energetic cost of mismatch.

Non-resonant behavior (parasitic power draw or phase deviation) becomes energetically unfavorable, forcing automatic degradation of Q and finally subsystem isolation via the Barrier protocol.

This converts “ethics-as-stability” into a strictly physical control law:
mismatch → loss → Q decay → isolation.

No policy layer is allowed to override this chain.
