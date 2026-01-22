01_TECH_SPEC — AMNION-ORACLE (Engineering Specification)

Project: AMNION-ORACLE  
Type: Open engineering specification (documentation repository)  
Scope: Software + Hardware + Gel chemistry (concept-level reference)  
Status: Concept / Engineering Spec (NOT a medical device, NOT clinical)


1) Purpose

AMNION-ORACLE is a resonance controller architecture intended as a reference model for:
- resonance-mode sensing
- phase / coherence tracking
- safety-first feedback control
- fail-safe decoupling and damping modes
- reproducible documentation structure for future prototyping

This repository contains specifications, not a finished product.


2) System Overview (3-layer structure)

The specification is organized into three technical domains:

1) SOFTWARE
   - control loop logic
   - sensor processing
   - decision logic
   - safety constraints / limit enforcement
   - logging and reproducibility

2) HARDWARE
   - sensing front-end (ADC, sampling)
   - actuator drivers
   - power / isolation
   - mechanical layout principles
   - EMI/grounding discipline

3) GEL CHEMISTRY
   - gel as resonance medium/interface
   - stability and repeatability requirements
   - constraints for safe experimentation (non-clinical)


3) Core Principle (Resonance Stability)

Medium = multi-layer ensemble of quantum fields, vacuum states, and condensed phases.  
Particles are stable excitations (modes) of the medium.  
Stability arises as an attractor where invariants are preserved and phase is retained.

Key engineering translation:

- Coherence is an operational metric (phase stability)
- Mismatch is the core enemy (phase drift / loss / dissipation)
- The controller’s job: **reduce mismatch, increase Q, enforce safety**


4) Canonical Controller Loop

At each cycle:

1) Read sensors (signal acquisition)
2) Estimate phase / mismatch indicators
3) Compute control output (gain/drive)
4) Enforce safety limits
5) Apply actuator commands
6) Log state + metrics

This forms a closed loop:

Sense → Estimate → Decide → Limit → Actuate → Log → Repeat


5) Stability Metrics (minimal set)

5.1 Phase mismatch
- `mismatch_phase = |φ - φ_avg|`  (or a robust norm)
- alternative: `sin(φ - φ_avg)` for periodic behavior

5.2 Power mismatch
- `mismatch_power = P_draw - P_in`

5.3 Loss
- `E_lost ∝ mismatch²`

5.4 Quality factor evolution
- if mismatch grows, then:
  - `dQ/dt < -δ · mismatch² · Q`
- if mismatch decreases:
  - `Q ↑` (coherence increases)


6) Safety Logic (non-negotiable)

6.1 Never allow uncontrolled negative Q drift
Use floor + damping:

- `current_Q = max(Q_min, current_Q + delta_Q)`
or
- `current_Q *= exp(-δ * loss)`

6.2 Avoid hard cutoffs (prevents oscillation “saw”)
Hard cutoff creates vibration at the limit.

Use:
- saturator
- soft throttle
- gain reduction near P_max

6.3 Fail-safe mode (Barrier)
Barrier is not “magic phase shift”.
Barrier is engineering reality:

Barrier = decouple + damp + cap
- cut coupling: `γ → 0`
- increase damping: `ζ ↑`
- enforce power budget cap: `P_budget`


7) Minimal Implementation Modules

7.1 Sensor Layer
- sampling scheduler
- calibration
- noise estimate
- baseline reference

7.2 Estimator Layer
- phase estimator (PLL-like)
- mismatch computation
- stability scoring

7.3 Controller Layer
- drive/gain computation
- soft limits
- integrator anti-windup

7.4 Safety Layer (FractalGuard)
- invariant check
- limit check
- emergency barrier
- cooldown & recovery

7.5 Logging Layer
- timestamped logs
- configuration hash
- reproducibility manifest
- event markers


8) Non-medical Disclaimer

This repository:
- is NOT medical advice
- is NOT a medical device description
- is NOT a treatment protocol
- provides only engineering abstraction and safety-first architecture
- does not provide instructions for diagnosing, treating, curing, or preventing diseases



9) Next Files (planned)

- `02_SOFTWARE_MODEL.md` — software architecture and pseudo-code
- `03_HARDWARE_MODEL.md` — hardware architecture (sensors/actuators/power)
- `04_GEL_CHEM_SPEC.md` — gel chemistry spec (conceptual constraints)
- `05_SAFETY_GUARD.md` — limit logic + barrier modes
- `06_FLOWCHART.md` — controller flowchart (Mermaid, GitHub-safe syntax)
- `07_TEST_PROTOCOL.md` — non-clinical test methodology (engineering)


End of file.
