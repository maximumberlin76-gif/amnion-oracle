# hardware/enclosure.md — AMNION-ORACLE (Enclosure & Structural Layer)

Project: AMNION-ORACLE  
Type: Hardware specification (engineering layer)  
Status: Concept-level (non-clinical, non-certified)

---

## Non-medical disclaimer

This document defines structural and material properties only.  
No biological, therapeutic, or medical effects are claimed.

---

## 1) Purpose

The enclosure defines:

- mechanical stability
- resonance boundary conditions
- thermal envelope
- interaction surface for gel medium

---

## 2) Base Material

Recommended class:

- Titanium alloy: Ti-6Al-4V
- Alternative: Grade 2 titanium

### Properties (reference)

| Parameter | Value |
|----------|------|
| Density | ~4.4 g/cm³ |
| Elastic modulus (E) | ~110 GPa |
| Yield strength (σ_yield) | 800–900 MPa |

---

## 3) Porous Structure

### Purpose

- reduce mass
- increase damping
- support gel retention
- prevent standing-wave amplification

### Geometry

Recommended:

- TPMS (Gyroid)
- or stochastic foam

### Parameter ranges

| Parameter | Range |
|----------|------|
| Porosity | 30–60 % |
| Pore size | 50–300 µm |
| Strut thickness | ≥ 0.1–0.5 mm |

### Constraints

- no straight-through channels
- continuous surface (no isolated volumes)

Structural condition:

σ ≤ 0.5 * σ_yield

---

## 4) Resonance Boundary Behavior

Design rule:

- enclosure must act as passive filter, not amplifier

### Conditions

- narrow-band response allowed
- broadband amplification forbidden

### Damping behavior

D_eff ≥ D_min

---

## 5) Thermal Envelope

| Parameter | Range |
|----------|------|
| T_min | 0 °C |
| T_max | 60 °C |

Constraints:

- no structural deformation
- no coating delamination
- no gel instability

---

## 6) Mechanical Load Limits

Static:

σ ≤ 0.5 * σ_yield

Cyclic (fatigue):

Σ (n_i / N_i) < 1.0

---

## 7) Interface with Gel Layer

Requirements:

- no chemical reaction
- no swelling-induced stress
- no micro-cracking

---

## 8) Manufacturing (concept-level)

Allowed processes:

- SLM / DMLS
- CNC finishing
- surface treatment

---

## 9) Validation

Minimum checks:

- structural integrity
- pore uniformity
- resonance sweep
- thermal stability

---

## 10) Engineering Summary

stability > damping > resonance response > efficiency
