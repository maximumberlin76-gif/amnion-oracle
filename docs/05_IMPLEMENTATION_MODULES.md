05_IMPLEMENTATION_MODULES — AMNION-ORACLE

Project: AMNION-ORACLE  
Type: Minimal implementation modules + interfaces  
Status: Documentation-first (no clinical use)

0. Non-medical / non-clinical disclaimer

AMNION-ORACLE is a concept-level engineering reference.  
It is **NOT** a medical device and **NOT** intended for clinical use.


1. Purpose

Define minimal modules required to implement AMNION-ORACLE as:
- simulator-only reference (recommended first)
- host controller + MCU firmware (optional)
- fully embedded control loop (advanced)

Main goal:
- strict module boundaries
- deterministic logs
- testability
- safety-first guard logic


2. Module list (minimal)

M0 — Config + Constants
Role: canonical parameters, thresholds, weights, limits  
Inputs: none  
Outputs: config object + `config_hash`

Requirements:
- text-based config (YAML/JSON)
- deterministic hash of config
- versioned schema


M1 — Sensors / Inputs (Acquisition Layer)
Role: capture raw signals  
Inputs: sensor streams / simulated streams  
Outputs: `raw_input_frame`

Fields (suggested):
- phase estimate inputs
- power inputs
- environmental noise proxy
- timestamps

Notes:
- can be simulated fully
- must handle missing / invalid sensors


M2 — Preprocessing / Filtering
Role: clean signals, stabilize estimates  
Inputs: `raw_input_frame`  
Outputs: `signal_frame`

Includes:
- smoothing filters
- outlier rejection
- interpolation (if safe)
- timestamp alignment


M3 — State Estimator
Role: estimate hidden states for control  
Inputs: `signal_frame`  
Outputs: `state_frame`

States (suggested):
- `phi` (current phase)
- `phi_avg` (reference)
- `C` (coherence)
- `Q` (retention factor)
- `noise_level`


M4 — Metrics Engine
Role: compute stability metrics  
Inputs: `state_frame` + `power_frame`  
Outputs: `metrics_frame`

Metrics:
- `mismatch_power`
- `mismatch_phase`
- `C`
- `Q`
- stability score `S`

This module must match:
- `04_STABILITY_METRICS.md`


M5 — Controller Core
Role: produce control output  
Inputs: `state_frame` + `metrics_frame` + config  
Outputs: `control_frame`

Control output examples:
- power draw request
- coupling coefficient (γ)
- damping coefficient (ζ)
- gain vector (α)

Hard rule:
- outputs must always be clamp-safe (no runaway)


M6 — Safety Logic (Guard / Barrier)
Role: override control outputs in unsafe conditions  
Inputs: `metrics_frame` + `state_frame` + config  
Outputs: `guard_frame` + patched `control_frame`

Guard states (example):
- `NORMAL`
- `THROTTLE`
- `DAMP`
- `DECOUPLE`
- `BARRIER`
- `SAFE_SHUTDOWN`

Canonical barrier behavior:
- decouple + damp + cap power budget

Must match:
- `03_SAFETY_LOGIC.md`


M7 — Actuator / Output Layer
Role: apply control to the system (real or simulated)  
Inputs: `control_frame`  
Outputs: actuator signals / simulator update

Notes:
- in simulation: updates system state
- on hardware: PWM/DAC/driver interface


M8 — Logger (Deterministic)
Role: write one-line deterministic logs  
Inputs: all frames  
Outputs: log stream

Requirements:
- one tick = one JSON line
- stable float rounding
- stable key order
- include `config_hash`
- allow hash-chain option


3. Interface contracts

Frames (recommended)
- `raw_input_frame`
- `signal_frame`
- `state_frame`
- `power_frame`
- `metrics_frame`
- `control_frame`
- `guard_frame`

Each frame:
- must include timestamp/tick
- must be serializable
- must support deterministic replay


4. Minimal build variants

Variant A — Simulator-only (recommended)
Modules:
- M0, M1(sim), M2, M3, M4, M5, M6, M7(sim), M8

Variant B — Host control + MCU
Modules:
- host: M0, M2, M3, M4, M5, M6, M8
- MCU: M1, M7

Variant C — Fully embedded
Modules:
- all on MCU: M0..M8 (light versions)


5. Notes

- Implementation language is not prescribed (Python/Node/C++).
- Documentation must remain source-of-truth.
- Build must be testable under missing sensors and noisy inputs.
- 
