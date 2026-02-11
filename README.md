Markdown
# AMNION-ORACLE

Documentation-first **resonance wellness capsule** architecture (software + hardware + gel chemistry),
with a controlled **ethics–physics safety loop**.

> **Important:** This repository is an **engineering prototype specification**.
> It is **NOT** medical advice, **NOT** a medical device, and **NOT** a treatment protocol.

---

## What this is

**AMNION-ORACLE** is an open engineering spec for a **resonance-based wellness capsule prototype**:
- **Software:** reference control loop + safety state machine
- **Hardware:** sensors / actuators / enclosure notes (planned)
- **Gel chemistry:** composition and handling spec (planned)
- **Validation:** test protocols, logging, and reproducible runs

The goal is to document a **control architecture** that can run reproducible “ticks” and produce logs,
so anyone can verify behavior and safety logic.

---

## Status

- **Stage:** Concept / Engineering Specification
- **Repo type:** Open documentation + reference controller architecture
- **Clinical status:** No clinical validation, no medical use

---

## Safety & Scope (read first)

- This repository is **NOT medical advice**
- This repository is **NOT a medical device**
- This repository is **NOT a treatment protocol**
- Nothing here should be used to diagnose, treat, cure, or prevent any disease
- Any future prototypes (if any) must comply with:
  - applicable law and regulations
  - certified laboratories
  - independent safety and ethics review

---

## Repository structure

- `/docs` — diagrams, flowcharts, rationale  
- `/configs` — configuration files (YAML)  
- `/controller` — controller architecture (interfaces, state machine, safety logic)  
- `/tests` — test protocols  
- `/schemas` — data/config schemas  
- `/tools` — helper utilities  
- `/examples` — usage examples  

## Core Engine (External Runtime)

This repository can integrate with the external SCM / Law-X runtime:

https://github.com/maximumberlin76-gif/<repo-name>

### Planned / future folders

- `/specs` — formal specifications  
- `/hardware` — enclosure/materials/sensors  
- `/gel` — gel chemistry specification  
- `/safety` — hazards, risk controls, safety test protocols  

---

## Quick Start (reference controller)

### 1) Read first (no execution)
- Configuration example: `configs/default.yaml`
- Control flow diagram: `docs/10_FLOWCHART.mmd`
- Controller entrypoint: `controller/__main__.py`
- Controller logic: `controller/amnion_controller.py`
- Config loader: `controller/config_loader.py`


### 2) Run (Linux/macOS / Git Bash / WSL)
```sh
git clone https://github.com/maximumberlin76/amnion-oracle.git
cd amnion-oracle
pip install -r requirements.txt
chmod +x run.sh
./run.sh


3) Run (Windows PowerShell)
'''Powershell
git clone https://github.com/maximumberlin76/amnion-oracle.git
cd amnion-oracle
pip install -r requirements.txt
python -m controller --config-dir configs --ticks 3000
4) Output
Execution logs are written to:
results/run_3000.log


License
Apache-2.0

Attribution
Concept & author: Maksym Marnov (maximumberlin76-gif)
GitHub: https://github.com/maximumberlin76-gif
