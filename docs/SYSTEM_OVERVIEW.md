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

## Documentation map
Primary docs are in `/docs`:
- `02_ARCHITECTURE.md` — architecture overview
- `03_SAFETY_LOGIC.md` — safety logic principles
- `04_STABILITY_METRICS.md` — metrics and thresholds
- `09_TEST_PROTOCOLS.md` — test procedures
- `10_FLOWCHART.mmd` — flow diagram (mermaid)
- `12_ETHICS_AND_INVARIANTS.md` — invariants and constraints

## Deliverable goal
Make this repository usable as an engineering base where:
- structure is clear
- state machine is unambiguous
- specs are formal enough to re-implement
- nothing depends on narrative context
