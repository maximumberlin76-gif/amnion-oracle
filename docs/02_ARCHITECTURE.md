AMNION-ORACLE — System Architecture

Project: AMNION-ORACLE  
Type: Documentation-first engineering specification (repository)  
Scope: Software + Hardware + Gel chemistry (concept-level reference)  
Status: Concept / Engineering Spec (NOT a medical device, NOT clinical)


1) Architectural intent

AMNION-ORACLE is a resonance controller architecture: a modular system that stabilizes and steers resonance modes in a coupled medium using a closed-loop pipeline:

sense → preprocess → estimate → metrics → guard → control → actuate → log

Tick-cycle (canonical, one line):

sense → preprocess → estimate → metrics → guard → control → actuate → log

Core goals
- Stability first (no runaway oscillations, no uncontrolled feedback)
- Deterministic safety logic (hard limits + soft dampers)
- Traceable control (logs, metrics, reproducible behavior)
- Modular interchangeability (hardware/firmware/software blocks evolve independently)


2) System topology (high level)

AMNION-ORACLE uses a layered pipeline:

2.1 Sensing layer
- Signal acquisition (analog/digital)
- Calibration + de-noising
- Feature extraction inputs (spectral + phase)

2.2 Resonance model layer
- State estimation (mode amplitudes, phase, coherence)
- Mode attribution (dominant nodes, harmonics)
- Drift detection (slow vs fast changes)

2.3 Safety + policy layer (gates)
- Allowed envelope checks
- Rate-of-change constraints
- Saturators / dampers / decoupling logic
- Emergency freeze / rollback behavior

2.4 Actuation layer
- Controlled output channels (field / waveform / mechanical / thermal / etc.)
- Closed-loop adjustment with bounded gain

2.5 Telemetry + integrity layer
- Logs + hashes
- Audit trail
- Offline export (SafeNet workflow)


3) Primary modules

3.1 Sensor Front-End (SFE)
Responsibilities
- Acquire raw signal(s)
- Pre-process (filtering, ADC integrity checks)
- Output stable data frames

Output
- `frame(t) = { samples[], fs, timestamp, sensor_meta }`

3.2 Spectral + Phase Analyzer (SPA)
Responsibilities
- FFT / wavelet spectrum
- Phase tracking (PLL-like logic)
- Coherence estimation

Core outputs
- Dominant frequency set: `F = { f_i }`
- Phase per mode: `φ_i`
- Coherence: `C(t)` in `[0..1]`

3.3 Resonance State Estimator (RSE)
Responsibilities
- Maintain the system state vector
- Detect drift / coupling changes

State example
- `S(t) = { A_i(t), φ_i(t), C(t), Δf_i(t), drift(t) }`

3.4 Stability Guard (SG) — non-negotiable safety wall

Functions
- Clamp energy injection
- Prevent negative-Q collapse or runaway-Q explosion
- Enforce soft transitions (avoid “hard cutoff saw”)
- Emergency Decouple + Damp + Cap (Barrier mode)

Guard state flow (text diagram, no graphics)

Inputs: metrics_frame + state_frame + config
Output: guard_state + patched control limits (clamp/throttle/decouple/damp/cap)

S0 NORMAL
  -> S1 THROTTLE      when mismatch exceeds warn thresholds OR coherence trending down
  -> S2 BARRIER       when severe mismatch OR sensor failure OR Q <= Q_crit
  -> S3 SAFE_HALT     when repeated barrier entries OR coherence collapse OR multiple sensor faults

S1 THROTTLE
  action: reduce G, reduce K, increase D, lower P_budget (soft)
  -> S0 NORMAL        when metrics return inside envelope for N consecutive ticks
  -> S2 BARRIER       when thresholds are crossed harder OR instability persists

S2 BARRIER (Decouple + Damp + Cap)
  action: K -> 0 (decouple), D -> high, P_budget -> minimum, freeze fast adaptation loops
  -> S1 THROTTLE      when stabilized and coherence recovers above floor for N ticks
  -> S3 SAFE_HALT     when barrier repeats too often OR sensors remain invalid

S3 SAFE_HALT (locked safe mode)
  action: stop active actuation, keep monitoring + logging only
  -> S0 NORMAL        manual restart only


Canonical rules
- `mismatch_power = P_draw - P_in`
- `mismatch_phase = |φ - φ_avg|` or `sin(φ - φ_avg)`
- `Q(t)` never goes negative by design

Barrier mode
- decouple coupling: `γ_i → 0`
- increase damping: `ζ ↑`
- cap power: `P_budget`

3.5 Control Policy Engine (CPE)
Responsibilities
- Translate state → bounded control action
- Use saturator + throttle logic near limits
- Keep the system inside an envelope (stable attractor)

Control action
- `u(t) = f(S(t), envelope, safety_state)`

3.6 Actuator Output Layer (AOL)
Responsibilities
- Generate waveform / field pattern / actuator command
- Apply smoothing to prevent discontinuities
- Provide actuation feedback telemetry

3.7 Telemetry + Integrity (TI)
Responsibilities
- Log key metrics
- Export reproducible trace packages
- Hash manifests for integrity

Artifacts
- `run_log.jsonl`
- `metrics.csv`
- `sha256sum.txt`
- detached signature (optional, future)

4) Data flow and interfaces

4.1 Frame protocol
- Raw: `frame.raw`
- Clean: `frame.clean`
- Features: `frame.features`
  
4.2 Minimal API shape

    sense() → frame
    preprocess(frame) → features
    estimate(features) → state
    metrics(state) → metrics_frame
    guard(state, metrics_frame) → guarded_state
    control(guarded_state) → control_action
    actuate(control_action)
    log(frame, state, metrics_frame, control_action)

5) Safety envelopes (concept)

Safety is expressed as an envelope, not a single threshold:

- power: `0 ≤ P_draw ≤ P_max`
- phase mismatch: `|Δφ| ≤ φ_max`
- coherence: `C_min ≤ C(t) ≤ 1`
- Q-factor bounded: `Q_min ≤ Q(t) ≤ Q_max`
- rate limits: `|dA/dt|`, `|dφ/dt|`, `|dP/dt| ≤ limits`

All policies must obey SG.


6) Stability strategy (why this won’t explode)

Key stabilizers:
- Soft saturation near limits (no step discontinuities)
- Gain reduction when approaching `P_max`
- Decoupling + damping in Barrier mode
- Coherence floor (no control when coherence collapses)
- Rate-of-change constraints to prevent control oscillations


7) Implementation notes (minimal / portable)

This repository is documentation-first. Implementation can be realized as:
- MCU firmware + host (Python/Node)
- Fully embedded control loop
- Simulator-only mode (for testing)

Portability principles:
- Strict module boundaries
- Text-based configs
- Deterministic logs + hashes


8) Non-medical disclaimer

AMNION-ORACLE is a concept-level engineering reference. It is NOT a medical device and NOT intended for clinical use.


9) Docs roadmap
- `03_SAFETY_LOGIC.md` — formal guard rules + barrier behavior
- `04_STABILITY_METRICS.md` — coherence/Q/power mismatch measures
- `05_IMPLEMENTATION_MODULES.md` — minimal module specs + interfaces
- `06_TEST_PROTOCOLS.md` — simulation plan and verification checks
