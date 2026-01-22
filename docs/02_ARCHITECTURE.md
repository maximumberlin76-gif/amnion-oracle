02_ARCHITECTURE — AMNION-ORACLE (System Architecture)

Project: AMNION-ORACLE  
Type: Open engineering specification (documentation repository)  
Scope: Software + Hardware + Gel chemistry (concept-level reference)  
Status: Concept / Engineering Spec (NOT a medical device, NOT clinical)


1. Architectural intent

AMNION-ORACLE is designed as a resonance controller architecture:  
a modular system that stabilizes and steers resonance modes in a coupled medium
(sensor → inference → actuation), with strict safety gating and traceable behavior.

Core goals:
- Stability first (no runaway oscillations, no uncontrolled feedback)
- Deterministic safety logic (hard limits + soft dampers)
- Traceable control (logs, metrics, reproducible behavior)
- Modular interchangeability (hardware/firmware/software blocks may evolve independently)


2. System topology (high level)

AMNION-ORACLE uses a layered pipeline:

1) Sensing layer
- Signal acquisition (analog/digital)
- Calibration + de-noising
- Feature extraction (spectral + phase)

2) Resonance model layer
- State estimation (mode amplitudes, phase, coherence)
- Mode attribution (dominant nodes, harmonics)
- Drift detection (slow vs fast changes)

3) Safety + policy layer (gates)
- Allowed envelope checks
- Rate-of-change constraints
- Saturators / dampers / decoupling logic
- Emergency freeze / rollback behavior

4) Actuation layer
- Controlled output channels (field / waveform / mechanical / thermal / etc.)
- Closed-loop adjustment with bounded gain

5) Telemetry + integrity layer
- Logs + hashes
- Audit trail
- Offline export (for SafeNet workflow)


3. Primary modules

3.1 Sensor Front-End (SFE)
Responsibilities:
- Acquire raw signal(s)
- Pre-process (filtering, ADC integrity checks)
- Output stable data frames

Outputs:
- `frame(t) = {samples[], fs, timestamp, sensor_meta}`


3.2 Spectral + Phase Analyzer (SPA)
Responsibilities:
- FFT / wavelet spectrum
- Phase tracking (PLL-like logic)
- Coherence estimation

Core outputs:
- Dominant frequency set: `F = {f_i}`
- Phase per mode: `φ_i`
- Coherence: `C(t)` (0..1)


3.3 Resonance State Estimator (RSE)
Responsibilities:
- Maintain system state vector
- Detect drift / coupling changes

State example:
- `S(t) = {A_i(t), φ_i(t), C(t), Δf_i(t), drift(t)}`


3.4 Stability Guard (SG)
This is the non-negotiable safety wall.

Functions:
- Clamp energy injection
- Prevent negative-Q collapse or runaway-Q explosion
- Enforce soft transitions (avoid “hard cutoff saw”)
- Emergency decouple/damp/cap (Barrier mode)

Rules (canonical):
- `mismatch_power = P_draw - P_in`
- `mismatch_phase = |φ - φ_avg|` or `sin(φ - φ_avg)`
- `Q(t)` never “dives negative” by design

Barrier mode:
- decouple coupling: `γ_i → 0`
- increase damping: `ζ ↑`
- cap power: `P_budget`



3.5 Control Policy Engine (CPE)
Responsibilities:
- Translate state → bounded control action
- Use saturator + throttle logic near limits
- Keep system inside envelope (stable attractor)

Control action:
- `u(t) = f(S(t), envelope, safety_state)`



3.6 Actuator Output Layer (AOL)
Responsibilities:
- Generate waveform / field pattern / actuator command
- Apply smoothing to prevent discontinuities
- Provide actuation feedback telemetry


3.7 Telemetry + Integrity (TI)
Responsibilities:
- Log all key metrics
- Export reproducible trace packages
- Hash manifests for integrity

Artifacts:
- `run_log.jsonl`
- `metrics.csv`
- `sha256sum.txt`
- detached signature (optional, future)


4. Data flow and interfaces

4.1 Frame protocol
- Raw: `frame.raw`
- Clean: `frame.clean`
- Features: `frame.features`

4.2 Minimal API shape
- `sense() → frame`
- `analyze(frame) → features`
- `estimate(features) → state`
- `guard(state) → allowed_state`
- `policy(allowed_state) → control_action`
- `actuate(control_action)`



5. Safety envelopes (concept)

Safety is expressed as **an envelope**, not as a single threshold:

- power: `0 ≤ P_draw ≤ P_max`
- phase mismatch: `|Δφ| ≤ φ_max`
- coherence: `C_min ≤ C(t) ≤ 1`
- Q-factor bounded: `Q_min ≤ Q(t) ≤ Q_max`
- rate limits: `|dA/dt|, |dφ/dt|, |dP/dt| ≤ limits`

All policies must obey SG.


6. Stability strategy (why this won’t explode)

Key stabilizers:
- Soft saturation near limits (no step discontinuities)
- Gain reduction when approaching `P_max`
- Decoupling + damping in Barrier mode
- Coherence floor (no control when coherence collapses)
- Rate-of-change constraints to prevent control oscillations



7. Implementation notes (minimal / portable)

This repository is documentation-first.
Implementation can be realized as:
- MCU firmware + host (Python/Node)
- Or fully embedded control loop
- Or simulator-only mode (for testing)

Portability principles:
- Strict module boundaries
- Text-based configs
- Deterministic logs + hashes


8. Non-medical disclaimer

AMNION-ORACLE is a concept-level engineering reference.
It is **NOT** a medical device and **NOT** intended for clinical use.


9. Roadmap (docs)

Next docs in this repository:
- `03_SAFETY_LOGIC.md` — formal guard rules + barrier behavior
- `04_STABILITY_METRICS.md` — coherence/Q/power mismatch measures
- `05_IMPLEMENTATION_MODULES.md` — minimal module specs + interfaces
- `06_TEST_PROTOCOLS.md` — simulation plan and verification checks
  
