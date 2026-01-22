AMNION-ORACLE

Open engineering specification (software + hardware + gel chemistry) for the AMNION-ORACLE resonance controller.

Status
- Stage: Concept / Engineering Spec (no clinical validation)
- Repo type: Open documentation + reference controller architecture (non-medical, non-clinical)

Safety & Scope (Read first)
- This repository is NOT medical advice, NOT a medical device, and NOT a treatment protocol.
- No instructions here should be used to diagnose, treat, cure, or prevent any disease.
- Any future prototypes (if any) must follow legal/ethical requirements, certified labs, and independent safety review.

Repository structure
- `/docs` — diagrams, flowcharts, rationale
- `/specs` — formal specifications (YAML + markdown)
- `/controller` — controller architecture (interfaces, state machine, safety logic)
- `/hardware` — enclosure/materials/sensors
- `/gel` — gel chemistry spec (requirements/tolerances/tests)
- `/safety` — hazards, risk controls, test protocols

Quick start (for readers)
1) Read: `specs/system.yaml`
2) Review controller flow: `docs/flowchart.md`
3) See controller spec: `controller/controller.yaml`

License
Apache-2.0

Attribution
Concept & author: Maksym Marnov
(maximumberlin76-gif)
