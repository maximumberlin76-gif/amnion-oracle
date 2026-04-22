# hardware/power_system.md — AMNION-ORACLE (Power System)

Project: AMNION-ORACLE  
Type: Hardware specification (power and safety layer)  
Status: Concept-level (non-clinical)

---

## Non-medical disclaimer

This document defines power constraints and safety behavior only.  
No biological or therapeutic claims are made.

---

## 1) Purpose

The power system defines:

- energy input limits  
- distribution constraints  
- safety interlocks  
- hardware-level enforcement  

Goal:

predictable and bounded energy behavior

---

## 2) Design principle

Priority:

safety > stability > continuity > efficiency

Power system must remain deterministic and enforce limits regardless of software state.

---

## 3) Power model

Definitions:

- P_in — input power  
- P_draw — consumed power  
- P_max — hardware maximum  
- P_budget — allowed operational budget  

Constraint:

P_draw ≤ P_max

---

## 4) Operating modes

Nominal:

P_draw ≤ P_budget_nominal  

Throttle:

reduced duty cycle  

Degraded:

minimal safe operation  

Lock:

no power to actuators  

---

## 5) Hard limits (non-negotiable)

P_draw ≤ P_max  
V_min ≤ V ≤ V_max  
I ≤ I_max  

These are enforced at hardware level.

---

## 6) Soft limiting

Smooth saturation:

S = 1 - (P_draw / P_max)^2  

Applied to control gain:

G_eff = G * S  

Purpose:

prevent oscillation and hard cut instability

---

## 7) Protection mechanisms

Required:

- fuse / breaker logic  
- watchdog timer  
- brownout detection  
- overcurrent protection  

---

## 8) Brownout behavior

If supply drops:

V < V_min → SAFE_SHUTDOWN  

System must not attempt recovery automatically.

---

## 9) Watchdog behavior

If control loop stalls:

tick_miss > N_max → HARD_DISABLE  

No delayed response allowed.

---

## 10) Thermal constraints

Power must respect thermal envelope:

T ≤ T_max  

If exceeded:

reduce power → then shutdown if persistent  

---

## 11) Failure modes

- power spike  
- uncontrolled draw  
- voltage collapse  
- thermal runaway  

Response hierarchy:

Throttle → Degrade → Lock  

---

## 12) Validation

Required tests:

- max load stability  
- power clamp trigger  
- brownout response  
- watchdog trigger  

Outputs:

- P_draw curve  
- shutdown threshold  
- recovery behavior  

---

## 13) Engineering rule

power is always bounded  

no subsystem may bypass hardware limits  

software cannot override safety constraints
