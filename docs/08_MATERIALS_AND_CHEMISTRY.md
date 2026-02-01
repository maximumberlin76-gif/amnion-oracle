08_MATERIALS_AND_CHEMISTRY — AMNION-ORACLE (Materials & Chemistry)

Project: AMNION-ORACLE  
Type: Materials & chemistry specification (concept-level)  
Status: Reference specification (NOT clinical)

Non-medical / non-clinical disclaimer  
AMNION-ORACLE is a concept-level engineering reference.  
It is NOT a medical device and NOT intended for clinical use.


1. Goals

- chemically stable structure
- long-term mechanical integrity
- predictable resonance behavior
- non-reactive interface with gel medium
- manufacturable with existing industrial processes


2. Structural frame (solid phase)

Recommended base material:

- Titanium alloy Ti-6Al-4V (medical/industrial grade)

Reasons:

- high strength-to-weight ratio  
- corrosion resistance  
- fatigue resistance  
- biocompatibility (reference property, not medical claim)

Key properties (typical):

- Yield strength σ_yield ≈ 800–900 MPa  
- Elastic modulus E ≈ 110 GPa  
- Density ≈ 4.4 g/cm³  


3. Porous lattice geometry

Purpose:

- reduce mass
- increase surface area
- provide mechanical damping
- support gel retention

Recommended topology:

- gyroid or TPMS lattice

Target ranges:

- pore size: 50–300 µm  
- porosity: 40–70 %

Rules:

- no straight-through channels
- continuous surface (no isolated islands)
- minimum strut thickness defined by σ <= 0.5 σ_yield


4. Surface coating (piezo / interface layer)

Optional thin-film coatings:

- Aluminum Nitride (AlN)  
- Zinc Oxide (ZnO)

Functions:

- piezoelectric coupling
- electrical isolation
- surface passivation

Thickness (concept):

- 100 nm – 5 µm


5. Gel medium (liquid / soft phase)

Role:

- signal transmission medium
- damping
- self-leveling contact

General requirements:

- electrically weakly conductive or tunable
- chemically stable
- low volatility
- non-corrosive

Conceptual composition:

- polymer hydrogel base
- solvent (water or non-aqueous)
- ionic or polar additives (trace level)

Rules:

- no aggressive acids/bases
- pH neutral to slightly buffered
- no gas formation under normal operation


6. Compatibility constraints

Frame ↔ coating:

- no galvanic corrosion
- matched thermal expansion where possible

Coating ↔ gel:

- no delamination
- no dissolution

Gel ↔ frame:

- no swelling-induced cracking
- no embrittlement


7. Thermal operating envelope

- T_min: 0 °C (concept)
- T_max: 60 °C (concept)

Rules:

- viscosity of gel must remain in stable range
- coating must not crack in thermal cycling


8. Aging and degradation

Design targets:

- no significant mechanical degradation < 10^7 cycles
- no phase separation of gel
- no coating peeling

If degradation detected:
- system must derate (reduce G, K)
- log degradation flag
- Guard layer may escalate to THROTTLE or BARRIER


9. Manufacturing notes (concept)

Possible processes:

- metal additive manufacturing (SLM/EBM)
- post-machining
- chemical vapor deposition (for coatings)
- vacuum impregnation (gel fill)

Quality checks:

- CT scan of lattice
- surface roughness measurement
- adhesion test of coating
- leak test after gel fill


10. Summary

Materials are chosen to favor:

- stability over performance
- predictability over maximum efficiency
- degradation that is slow and observable
