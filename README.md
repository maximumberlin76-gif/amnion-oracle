AMNION-ORACLE  
Documentation-first resonance control architecture.

System = Control Loop

Model → Act → Sense → Adjust

Error = Lie  
Any proxy-layer introduces entropy.

Validation = Effect  
If there is no physical feedback — there is no strategy.

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
- `/configs` — configuration files (YAML)  
- `/controller` — controller architecture (interfaces, state machine, safety logic)  
- `/tests` — test protocols  
- `/schemas` — data / config schemas  
- `/tools` — helper utilities  
- `/examples` — usage examples  

Planned / future folders

- `/specs` — formal specifications  
- `/hardware` — enclosure/materials/sensors  
- `/gel` — gel chemistry spec  
- `/safety` — hazards, risk controls, test protocols

Quick start (reference)

1) Read configuration:
   `configs/default.yaml`

2) Review controller flow:
   `docs/10_FLOWCHART.mmd`

3) See controller implementation:
   `controller/amnion_controller.py`

git clone https://github.com/maximumberlin76/amnion-oracle.git
cd amnion-oracle
chmod +x run.sh
./run.sh

License
Apache-2.0

Attribution
Concept & author: Maksym Marnov
(maximumberlin76-gif)
