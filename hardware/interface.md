# hardware/interface.md — AMNION-ORACLE (Hardware ↔ Controller Interface)

Project: AMNION-ORACLE  
Type: Interface specification  
Status: Concept-level (non-clinical)

---

## Non-medical disclaimer

This document defines interface contracts only.  
No biological or therapeutic effects are claimed.

---

## 1) Purpose

Define deterministic interface between:

- controller (software)
- hardware (sensors + actuators + power system)

Goal:

stable, auditable, and bounded interaction

---

## 2) Design principle

- hardware = source of truth (sensors)
- controller = decision layer
- hardware = final enforcement (actuators + power caps)

Controller must never bypass hardware limits.

---

## 3) Data flow

Sensors → SafetyGate → Runtime → Actuators

Each tick:

1. read sensors  
2. sanitize inputs  
3. evaluate safety  
4. compute control  
5. apply hardware limits  
6. log  

---

## 4) Sensor interface

Input format (example):

```json
{
  "P_in": float,
  "P_draw": float,
  "Q": float,
  "phase_error": float,
  "temp_c": float,
  "sensor_valid": bool
}
```

Rules:

- missing values → degraded mode  
- invalid values → barrier  
- no exceptions allowed  

---

## 5) Derived metrics

Computed in controller:

- mismatch_power = P_draw − P_in  
- mismatch_phase = |phase_error|  
- coherence_score  

All derived metrics must be deterministic.

---

## 6) Control output

Output format:

```json
{
  "u_control": float,
  "mode": "NORMAL | THROTTLE | BARRIER | LOCK",
  "P_budget": float
}
```

Rules:

- values must be bounded  
- no direct actuator override  
- no uncontrolled output  

---

## 7) Hardware enforcement

Before execution:

u_hw = clamp(u_control, u_min, u_max)

Power enforcement:

P_draw ≤ P_max

If violated:

→ HARD_DISABLE  

---

## 8) Safety interaction

SafetyGate produces:

- state  
- limits  
- patch  

Runtime must obey:

- patch parameters override control  
- safety state defines allowed behavior  

---

## 9) Failure handling

Case handling:

- sensor invalid → DEGRADE  
- power overflow → LOCK  
- phase instability → BARRIER  

Controller must not attempt unsafe recovery.

---

## 10) Timing

Requirements:

- fixed tick rate  
- deterministic execution  
- no uncontrolled async calls  

---

## 11) Logging

Each tick must include:

- inputs  
- outputs  
- state  
- limits  
- decision reason  

Goal:

full reproducibility

---

## 12) Validation

Tests:

- sensor failure simulation  
- power violation  
- phase instability  
- full loop replay  

Outputs:

- identical logs for identical inputs  
- correct state transitions  

---

## 13) Engineering rule

controller decides  
hardware enforces  

no layer may override safety
