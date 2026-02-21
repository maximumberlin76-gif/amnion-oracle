# RESONANCE_INTERFACE — Controller ↔ Model Boundary

Purpose

Defines how the controller calls the resonance model.

---

## Call Order inside tick()

Model → Act → Sense → Adjust

Model step:

coherence, S_next, diag =
    coherence_model(S_prev, metrics, dt, params)

---

## Allowed Data Flow

Controller → Model:
    metrics
    dt
    params

Model → Controller:
    coherence
    S_next
    diag

Forbidden:

- model writing logs
- model changing guard_state
- model accessing hardware IO

---

## Failure Policy

If model returns invalid value:

- clamp coherence to 0.0
- raise safety flag
- controller MAY escalate state
