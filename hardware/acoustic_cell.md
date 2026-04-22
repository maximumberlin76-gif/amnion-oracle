# hardware/acoustic_cell.md — AMNION-ORACLE (Acoustic / Resonance Cell)

Project: AMNION-ORACLE  
Type: Hardware specification (acoustic / resonance layer)  
Status: Concept-level (non-clinical, non-certified)

---

## Non-medical disclaimer

This document defines acoustic and geometric properties only.  
No biological, therapeutic, or medical effects are claimed or implied.

---

## 1) Purpose

The acoustic / resonance cell defines:

- internal resonance geometry
- cavity behavior
- passive frequency selection
- coupling between enclosure, gel layer, and internal structure

The cell is strictly passive.

---

## 2) Design principle

Priority:

stability > selectivity > resonance response > efficiency

The cell must never act as an uncontrolled amplifier.

---

## 3) Reference model (Helmholtz approximation)

f = (c / 2π) * sqrt(A / (V * L_eff))

Where:

- f — resonance frequency  
- c — speed of sound in medium  
- A — neck cross-section  
- V — cavity volume  
- L_eff — effective neck length  

Used only as first-order model.

---

## 4) Geometry

Base archetype:

- triangular / tetrahedral constraint geometry  
- optionally Helmholtz-like cavity behavior  

Rules:

- no straight-through channels  
- no uncontrolled multi-cavity resonance  
- geometry must enforce mode limitation  

---

## 5) Triangular cell (core unit)

Purpose:

- structural stability  
- resonance coherence  
- suppression of chaotic modes  

Constraints:

- symmetric or near-symmetric geometry  
- no degenerate angles  
- no collapse under load  

---

## 6) Resonance behavior

Allowed:

- one dominant resonance band  
- controlled harmonics  

Forbidden:

- broadband amplification  
- multi-peak instability  
- uncontrolled standing waves  

---

## 7) Parameters

- f_ref — target frequency  
- f_tol — tolerance  
- V — volume  
- A — aperture  
- L_eff — path length  
- Q_hw — quality factor  
- A_max — amplitude limit  

Constraint:

|f_cell − f_ref| ≤ f_tol

---

## 8) Safety constraints

Q_hw ≤ Q_hw_max  
A ≤ A_max  
|Δf| ≤ Δf_max_hw  

Violation → reduce gain OR HARD_DISABLE

---

## 9) Enclosure coupling

- no resonance-induced fracture  
- no structural amplification  
- no stress concentration  

Rule:

resonance < structural stability priority

---

## 10) Gel coupling

Gel affects:

- damping  
- resonance width  
- effective frequency  

Rule:

all calculations assume loaded state

---

## 11) Thermal behavior

Temperature affects resonance.

Requirement:

f_cell(T) must remain within safe band

Otherwise → derate

---

## 12) Failure modes

- resonance runaway  
- multi-peak instability  
- structural collapse  
- detuning  

Response:

reduce G  
increase D  
or HARD_DISABLE  

---

## 13) Validation

- frequency sweep  
- thermal sweep  
- amplitude test  
- drift test  

Outputs:

- peak frequency  
- Q factor  
- amplitude window  
- stability range  

---

## 14) Engineering rule

passive resonance allowed  
amplification forbidden
