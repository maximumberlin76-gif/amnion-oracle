# hardware/integration.md — AMNION-ORACLE (Hardware Integration Layer)

Project: AMNION-ORACLE  
Type: Hardware integration specification  
Status: Concept-level (non-clinical)

---

## Non-medical disclaimer

This document defines system-level integration only.  
No biological or therapeutic effects are claimed.

---

## 1) Purpose

This layer defines how subsystems interact:

- enclosure (mechanical stability)
- acoustic_cell (resonance structure)
- power_system (energy control)

Goal:

coherent, stable, and bounded system behavior

---

## 2) Integration principle

Priority:

safety > stability > coupling > performance

No subsystem may destabilize another.

---

## 3) Layer hierarchy

Top-level control order:

1. Power system (hard limits)
2. Safety logic (state machine)
3. Resonance behavior (acoustic cell)
4. Mechanical structure (enclosure)

Rule:

lower layers must obey upper constraints

---

## 4) Coupling rules

### 4.1 Power → Acoustic

- power defines maximum excitation
- acoustic cell cannot exceed power envelope

Constraint:

resonance amplitude ≤ power-defined limits

---

### 4.2 Acoustic → Enclosure

- resonance induces mechanical stress
- enclosure must absorb without amplification

Constraint:

no resonance mode may exceed structural tolerance

---

### 4.3 Power → Enclosure

- heat generation from power draw
- enclosure must dissipate heat safely

Constraint:

thermal envelope must not be exceeded

---

### 4.4 Gel coupling

- gel modifies resonance response
- gel affects damping and energy distribution

Rule:

all resonance calculations assume loaded state

---

## 5) Control loop interaction

Each tick:

1. sensors read system state
2. safety_gate evaluates constraints
3. runtime computes control output
4. power_system enforces limits
5. acoustic_cell responds passively

No step may bypass safety or power enforcement.

---

## 6) Failure propagation rules

If subsystem fails:

- acoustic instability → reduce gain
- power violation → HARD_DISABLE
- structural risk → BARRIER mode

Failure must not cascade uncontrolled.

---

## 7) Isolation behavior

System must support partial isolation:

- disable actuation
- maintain monitoring
- preserve logging

Goal:

graceful degradation instead of collapse

---

## 8) Thermal integration

Combined system must satisfy:

T_total ≤ T_max

Sources:

- power system heat
- resonance damping losses
- environmental input

---

## 9) Synchronization

All subsystems operate on a unified control tick.

Requirement:

- deterministic timing
- no asynchronous uncontrolled updates

---

## 10) Validation

Integration tests:

- full system sweep under load
- resonance under power constraints
- thermal + resonance combined test
- failure injection test

Outputs:

- system stability envelope
- failure response consistency
- recovery behavior

---

## 11) Engineering rule

no subsystem operates independently  

system stability is defined only at integration level
