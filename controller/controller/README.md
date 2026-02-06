# AMNION-ORACLE — Controller

This folder contains the reference controller loop for **AMNION-ORACLE**.  
It is a **documentation-first** safety/control architecture.

> **Non-medical / non-clinical disclaimer:**  
> AMNION-ORACLE is a concept-level engineering reference.  
> It is **NOT** a medical device and **NOT** intended for clinical use.

---

## What is inside

- `amnion_controller.py`  
  Main control loop orchestration (high-level controller logic).

- `config_loader.py`  
  Loads and validates configuration files (schema/bounds/safe defaults).

- `safety_gate.py`  
  Safety dominance layer. Enforces invariants, fails closed, escalates:
  `THROTTLE -> BARRIER -> SAFE_HALT`.

- `runtime.py`  
  Runtime utilities (ticks/timing/state management).

- `metrics.py`  
  Stability and audit metrics (counters, invariants, health scores).

- `logger.py`  
  Structured logging for traceability and auditability.

- `__init__.py`  
  Package marker.

---

## Design principles

- Assume hostile or imperfect reality: sensors may lie, freeze, drift, or disappear.
- No single layer is trusted.
- Safety must emerge from **physics + architecture**, not policy.
- Any ambiguity -> conservative behavior.
- Never “power through” uncertainty.

---

## Expected call graph (reference)

Typical execution flow:

1. `config_loader` loads config and validates bounds
2. `amnion_controller` starts the control loop
3. Each tick:
   - read inputs / sensor state (sim or adapter)
   - compute proposed control output
   - pass through `safety_gate`
   - emit actuation / command (or simulate it)
   - log + metrics update
4. If violations:
   - `THROTTLE` (reduce energy / slow down)
   - `BARRIER` (decouple / damping-first)
   - `SAFE_HALT` (stop and require manual restart)

---

## How to run (reference)

This repository may support multiple deployment modes:

- **Local simulator** (recommended first)
- **Host controller** (control loop + IO adapters)
- **Embedded target (future)**

Exact entrypoint depends on repo-level tooling.  
If you add a single entrypoint later, recommended pattern:

- `controller/__main__.py` (or `controller/run.py`) calls:
  - `load_config(...)`
  - `run_controller_loop(...)`

---

## Safety escalation contract

The controller must obey the safety gate output decision:

- `OK` -> proceed with output
- `THROTTLE` -> apply damping / reduce power / reduce aggressiveness
- `BARRIER` -> decouple / clamp / restrict acceptance band
- `SAFE_HALT` -> stop, lock state, require manual restart

No code path should bypass `safety_gate`.

---

## Logging & audit

Logging is mandatory, not optional.

Minimum expectations:

- append-only logs (preferred)
- deterministic, structured records
- optional hash manifest / hash chaining for tamper-evidence

A “successful defense” is not uptime at any cost.  
Success is:

- no uncontrolled actuation
- no runaway energy
- no silent corruption
- graceful degradation

---

## Notes

This controller is intended to be understandable, auditable, and reproducible.  
Performance optimizations must never weaken safety invariants.
