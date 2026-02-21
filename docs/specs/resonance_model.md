# RESONANCE_MODEL — AMNION-ORACLE (Deterministic Coherence Model)

Purpose

This document defines the deterministic resonance model layer.
The controller DOES NOT compute resonance physics directly.
It calls a dedicated model interface.

Design rule:
Controller = decision layer
Resonance Model = state evolution + coherence estimation

---

## State Vector (S-vector)

The model operates on a fixed-order state vector.

S = {
    phase,
    phase_noise,
    q_factor,
    damping,
    energy_proxy,
    temp_c,
    power_w,
    sensor_health,
    fault_count
}

Rules:

- order MUST be fixed
- no dynamic keys
- model MUST NOT read controller state directly

---

## Inputs

metrics:
    temp_c
    power_w
    phase_noise
    q_factor
    sensor_health

dt:
    controller tick delta time

params:
    model coefficients loaded from config

---

## Outputs

coherence_0_1
S_next
diag

Where:

coherence_0_1 — normalized stability metric [0..1]
S_next — next deterministic state vector
diag — optional debug fields (no side effects)

---

## Interface Contract

coherence_model(S, metrics, dt, params) ->
    (coherence_0_1, S_next, diag)

Constraints:

- pure function
- no randomness
- no IO
- identical inputs → identical outputs

---

## Determinism Rules

- fixed float precision policy
- fixed update order
- no time.now()
- no hidden global state

---

## Conceptual Model

The model approximates phase-coherence behavior.

Reference idea:

R = | (1/N) Σ exp(iθ_k) |

This repo MAY implement simplified proxies.
Exact physics is out of scope of this document.

---

## Responsibility Split

Model layer:

- evolves state
- estimates coherence

Controller:

- reads coherence
- decides state transitions
