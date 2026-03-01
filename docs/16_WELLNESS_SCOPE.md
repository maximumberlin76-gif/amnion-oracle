# 16_WELLNESS_SCOPE.md — AMNION-ORACLE (Wellness Scope)

Project: AMNION-ORACLE  
Document type: Scope definition (documentation-first)  
Status: Reference specification (NOT clinical)

## Non-medical / non-clinical disclaimer

AMNION-ORACLE is a concept-level engineering reference and prototype specification.  
It is NOT medical advice, NOT a medical device, and NOT a treatment protocol.  
No biological, therapeutic, diagnostic, or medical effects are claimed or implied.

This document defines *scope boundaries* for a wellness-oriented prototype capsule architecture.

## 1) Purpose of the “wellness” scope

In AMNION-ORACLE, **wellness** means:

- controlled environmental exposure (non-clinical)
- user comfort / relaxation support
- reproducible operation with transparent logs
- safety-first behavior under uncertainty (monotonic escalation)

Wellness here is an *engineering scope label*, not a medical claim.

## 2) What the system is

AMNION-ORACLE is an open engineering specification for a **resonance wellness capsule prototype**:

- software: deterministic control loop + safety state machine + logging
- hardware: sensors / actuators boundary + power and watchdog envelopes (concept-level)
- materials & gel chemistry: stability-focused specification (concept-level)
- validation: test protocols, deterministic replay, and audit trails

The central goal is **reproducible ticks** and **verifiable safety logic**, not “effects”.

## 3) What the system is NOT

AMNION-ORACLE is NOT:

- medical advice
- a medical device
- a clinical protocol
- a diagnostic tool
- a treatment or prevention method for any disease
- a substitute for professional healthcare

No part of this repository should be used to diagnose, treat, cure, or prevent any disease.

## 4) Allowed claims (documentation language)

Allowed descriptions in this repository are limited to:

- engineering architecture and boundaries
- deterministic control behavior
- safety state transitions and guards
- measured signals and derived metrics (e.g., coherence proxies)
- logging, replay, and audit integrity
- materials stability and handling constraints (non-biological)

Examples of acceptable phrases:

- “controlled exposure environment”
- “relaxation-support context” (non-clinical)
- “simulation-only run”
- “deterministic controller tick”
- “monotonic safety escalation”
- “materials stability / compatibility / storage constraints”

## 5) Disallowed claims (must not appear)

The following categories must not appear in documentation, code comments, README, or releases:

- “treats / cures / heals”
- “therapy / therapeutic”
- “medical-grade results”
- “clinically proven”
- “diagnosis”
- “prevents disease”
- any claim about biological outcomes or health improvements

If a phrase could be interpreted as a medical claim, it is disallowed.

## 6) Safety framing for a wellness prototype

Safety is defined as **engineering containment**:

- actuator output is clamped and bounded
- uncertain sensing escalates to safer states (THROTTLE → BARRIER → SAFE_HALT)
- no hidden behavior: logs are the source of truth
- deterministic replay must reproduce the same state transitions for the same inputs

Safety is a control property, not a medical statement.

## 7) Human role (user responsibility)

The system is designed as:

- an engineering prototype spec
- operated (if ever) only under applicable law and regulations
- evaluated (if ever) in certified labs with independent review

The user is responsible for compliance with local regulations and for not using this project as a medical device.

## 8) Interface with external runtimes (optional)

External runtimes (e.g., SCM / Law-X) are optional integrations.

- standalone mode remains valid and fully functional for simulation and specification purposes
- integrations must not add medical claims
- integrations must preserve deterministic logging and monotonic safety constraints

## 9) Summary

AMNION-ORACLE is a **wellness-oriented engineering specification** for a resonance capsule prototype.

- Scope: environment control + safety + reproducibility + audit
- Explicitly non-clinical
- No medical claims, now or later, inside this repository

If a statement is ambiguous between “engineering” and “medical”, treat it as medical and remove it.

