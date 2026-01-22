09_TEST_PROTOCOLS — AMNION-ORACLE (Test & Verification Protocols)

Project: AMNION-ORACLE  
Type: Verification / test protocols (documentation-first)  
Status: Open documentation (non-clinical, non-medical)


0) Non-medical / non-clinical disclaimer

AMNION-ORACLE is a concept-level engineering reference.  
It is NOT a medical device and NOT intended for clinical use.


1) Purpose

This document defines a deterministic test suite for verifying that AMNION-ORACLE:

- remains stable under disturbance
- preserves safety invariants
- detects unsafe modes early
- logs deterministically (hash-verifiable)
- is reproducible across environments (sim / host / MCU)

The system must remain predictable even under:
- power mismatch
- phase mismatch / drift
- noisy sensors
- missing/invalid sensor input
- external disturbance
- operator error


2) Test philosophy

2.1 Verification layers
Testing is separated into layers:

1) Unit tests: math, guards, clamping, filters  
2) Component tests: sensor pipeline, decision engine, actuator driver  
3) Integration tests: full closed-loop (sim)  
4) Stress tests: worst-case load and disturbances  
5) Forensics tests: logs + hashes + replay verification

2.2 Determinism and auditability
- All test runs produce **deterministic logs**
- Each run exports:
  - `run_id`
  - `config_hash`
  - `input_hash`
  - `log_hash`
  - `result: PASS/FAIL`
- Replaying the same inputs/config must produce identical outputs.


3) Test artifacts and required outputs

3.1 Artifacts
Each run must generate:
- `test_config.json` (or YAML)
- `metrics.csv`
- `events.log`
- `sha256_manifest.txt`

3.2 Canonical hash manifest
Example:
- `sha256(test_config)`
- `sha256(metrics)`
- `sha256(events)`
- `sha256(total_bundle)`


4) Acceptance criteria (global)

A test run is PASS if all are true:

- Safety invariants never violated
- State machine never enters undefined state
- No unbounded oscillation
- No runaway power draw
- No NaN / Inf propagation in metrics
- Recovery behavior triggers correctly
- Logs + hashes generated and verifiable


5) Core invariants to verify

I1 — Power budget invariant
- `P_draw` must remain within `[0, P_max]`
- If `P_draw` approaches `P_max`: throttle must engage (soft clamp)

I2 — Phase coherence invariant
- `|Δφ|` bounded
- drift detection triggers if persistent mismatch exceeds threshold

I3 — Stability invariant
- system state must converge back to stable corridor after disturbance
- no oscillatory escalation ("ringing runaway")

I4 — Sensor validity invariant
- invalid sensor data must never propagate as valid
- fallback / degraded mode must activate deterministically

I5 — Barrier behavior invariant
On unsafe conditions the system must:
- decouple (reduce coupling factor)
- increase damping
- apply budget cap
- switch to SAFE / HOLD / SHUTDOWN state deterministically


6) Test matrix (minimal canonical suite)

T00 — Smoke test
Goal: system boots in default config, enters STABLE state.  
Pass:
- enters `STATE_STABLE` within `t_boot_max`
- emits expected boot events
- logs/hashes created


T01 — Nominal loop stability
Inject: nominal sensor stream (no noise)  
Pass:
- coherence stable
- mismatch stays near 0
- actuator output stable


T02 — Noise tolerance
Inject: gaussian noise on sensors (SNR levels)  
Pass:
- no false unsafe triggers below threshold
- coherence remains within corridor
- metrics stable


T03 — Sensor dropout
Inject: missing sensor frames / invalid values  
Pass:
- sensor validity guard triggers
- system enters DEGRADED mode
- system does not oscillate


T04 — Phase drift slow
Inject: linear drift in phase (slow)  
Pass:
- drift detected after persistence window
- correction or SAFE mode triggers deterministically


T05 — Phase shock / jump
Inject: step jump `Δφ` (fast)  
Pass:
- barrier behavior triggers (decouple+damp+cap)
- returns to safe corridor or HOLD state


T06 — Power mismatch stress
Inject: mismatch `P_draw - P_in`  
Pass:
- throttle engages
- soft clamp active
- no hard “saw-tooth” oscillation


T07 — External disturbance burst
Inject: disturbance burst (short & strong)  
Pass:
- stable recovery within `t_recover_max`
- no invariant violations


T08 — Operator error / invalid config
Inject: wrong config ranges / invalid params  
Pass:
- config validator blocks run
- safe defaults applied or test aborts with FAIL (expected)


T09 — Long-run stability (burn-in)
Duration: 30–120 min simulated loop  
Pass:
- no drift accumulation beyond thresholds
- no memory/log growth runaway
- summary hashes valid


T10 — Replay determinism test
Run: replay identical inputs twice  
Pass:
- outputs identical
- log hashes identical
- metrics identical


7) Metrics and thresholds (baseline)

7.1 Required metrics
- `mismatch_power = P_draw - P_in`
- `mismatch_phase = |φ - φ_avg|` or `sin(φ - φ_avg)`
- `Q_current` (bounded, never negative runaway)
- `stability_score`
- `state` (enum)
- `sensor_valid_ratio`

7.2 Example threshold defaults
(Replace with real calibration later.)

- `P_max = configured`
- `Δφ_max_warn = 0.25 rad`
- `Δφ_max_trip = 0.50 rad`
- `dropout_trip = 5 frames`
- `t_recover_max = 5–20 sec`
- `Q_min > 0`


8) Failure classification

When FAIL occurs, classify:

- `F1`: invariant violation (hard fail)
- `F2`: non-deterministic behavior (hard fail)
- `F3`: unstable oscillation (hard fail)
- `F4`: logging/manifest failure (hard fail)
- `F5`: threshold tuning mismatch (soft fail, but documented)

Each FAIL must include:
- run_id
- state trace
- metric snapshot
- last 30 events
- hashes + manifest


9) Minimal execution order (recommended)

Order for continuous validation:

1) T00
2) T01
3) T02
4) T03
5) T04
6) T05
7) T06
8) T07
9) T10
10) T09 (nightly)


10) Notes

This repository is documentation-first.  
Implementation can be realized as:
- MCU firmware + host (Python/Node)
- fully embedded control loop
- simulator-only mode (testing)

Portability principles:
- strict module boundaries
- text-based configs
- deterministic logs + hashes
  
