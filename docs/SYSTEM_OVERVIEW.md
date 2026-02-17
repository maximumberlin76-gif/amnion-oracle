# SYSTEM_OVERVIEW

## What this repository is
**AMNION-ORACLE** is a documentation-first engineering specification for a resonance-oriented wellness capsule **controller architecture**:
- deterministic **control loop**
- explicit **safety state machine**
- reproducible **ticks + logs**
- test protocols and schemas

> Important: This repository is an engineering prototype specification.  
> It is **NOT** medical advice, **NOT** a medical device, and **NOT** a treatment protocol.

## Conceptual stack
**Capsule → Controller → Safety Loop → Environment → Feedback**

- **Capsule**: the bounded system concept (enclosure + sensors + optional materials/gel spec).
- **Controller**: deterministic runtime that executes ticks and transitions.
- **Safety Loop**: physics/stability constraints + ethics invariants encoded as hard limits.

## Control loop (reference)
**Model → Act → Sense → Adjust**

- **Model**: maintain internal state estimate and thresholds from config.
- **Act**: compute the next safe action (or no-op in simulation).
- **Sense**: ingest sensors (or simulated signals).
- **Adjust**: update state machine and log decisions.

## Determinism and auditability
A core requirement is **reproducible behavior**:
- same config + same inputs → same transitions
- logs capture: state, reason, thresholds, metrics, action decision
- no hidden side effects

## Safety model
Controller behavior is governed by a finite set of states:
- OK
- WARN
- THROTTLE
- ISOLATE
- DEGRADED
- LOCK

Transitions are defined explicitly (see `docs/STATE_MACHINE.md`), and enforced at runtime.

## Documentation Map (docs/)

This folder is the single source of truth for the AMNION-ORACLE specification.  
Read order: SYSTEM_OVERVIEW → STATE_MACHINE → the numbered documents.

- `SYSTEM_OVERVIEW.md` — top-level system summary, boundaries, and how docs connect.
- `STATE_MACHINE.md` — canonical controller states, transitions, triggers, and invariants mapping.

Numbered docs (primary specification series):
- `00_PREFACE.md` — intent, non-clinical boundary, and how to read the spec.
- `01_TECH_SPEC.md` — technical baseline, assumptions, inputs/outputs (concept-level).
- `02_ARCHITECTURE.md` — architecture overview: modules, interfaces, data flow.
- `03_SAFETY_LOGIC.md` — safety philosophy + enforcement logic (what blocks what).
- `04_STABILITY_METRICS.md` — stability metrics, thresholds, damping/Q concepts (non-clinical).
- `05_IMPLEMENTATION_MODULES.md` — implementation modules map (what exists, what is planned).
- `06_SOFTWARE_SPEC.md` — software behavior and reference controller specification.
- `07_HARDWARE_SPEC.md` — hardware scope: sensors/actuators/interfaces (spec-only).
- `08_MATERIALS_AND_CHEMISTRY.md` — materials/gel handling spec structure (no medical claims).
- `09_TEST_PROTOCOLS.md` — test plans, reproducible runs, logging expectations.
- `10_FLOWCHART.mmd` — mermaid flowchart diagram of the control loop and safety branches.
- `11_RELEASE_AND_DEPLOYMENT.md` — releases, versioning, reproducibility, packaging notes.
- `12_ETHICS_AND_INVARIANTS.md` — ethical axioms and hard invariants (enforced by controller).
- `13_THREAT_MODEL.md` — threat model, misuse cases, and defensive assumptions.
- `14_LIMITATIONS_AND_SCOPE.md` — explicit limits, non-goals, and out-of-scope items.
- `15_GLOSSARY.md` — glossary of terms and canonical naming.

## Deliverable goal
Make this repository usable as an engineering base where:
- structure is clear
- state machine is unambiguous
- specs are formal enough to re-implement
- Specifications must be sufficient for independent re-implementation.
