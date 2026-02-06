# 14_LIMITATIONS_AND_SCOPE — AMNION-ORACLE  
**Limitations & Scope**

Project: AMNION-ORACLE  
Type: Scope definition & limitations (documentation-first)  
Status: Reference specification (NOT clinical)

---

## Non-medical / non-clinical disclaimer

AMNION-ORACLE is a concept-level engineering reference.  
It is NOT a medical device and NOT intended for clinical use.

---

## Purpose

This document defines:

- what AMNION-ORACLE is designed to address  
- what it is explicitly NOT designed to address  
- boundaries of responsibility and applicability  

The goal is to prevent misinterpretation, overextension, and unsafe expectations.

---

## In-Scope (What AMNION-ORACLE Covers)

AMNION-ORACLE addresses:

- Resonant control loop architecture
- Safety-first state machine (THROTTLE / BARRIER / SAFE_HALT)
- Deterministic logging and auditability
- Simulation-first validation
- Hardware/software co-design principles
- Degradation-before-failure behavior
- Monotonic safety behavior

It focuses on:

- preventing runaway dynamics  
- preventing uncontrolled actuation  
- ensuring predictable failure modes  

---

## Out of Scope (What AMNION-ORACLE Does NOT Cover)

AMNION-ORACLE does NOT provide:

- Medical diagnosis or therapy
- Clinical decision support
- Autonomous weapon control
- General artificial intelligence
- Cryptographic security system
- Nation-state level cyber defense
- Human behavioral prediction

It is not a replacement for:

- regulatory certification
- domain-specific safety standards
- certified medical, aviation, or nuclear controllers

---

## Conceptual Nature

All models, equations, and materials described:

- are conceptual engineering references  
- may require adaptation for real hardware  
- are not validated against regulatory frameworks  

Any real-world implementation requires independent engineering verification.

---

## No Performance Guarantees

AMNION-ORACLE makes no claims regarding:

- optimal efficiency  
- maximum throughput  
- best-in-class performance  

Priority order:

1. Safety  
2. Predictability  
3. Stability  
4. Performance (last)

---

## No Autonomy Claim

AMNION-ORACLE:

- does not claim consciousness  
- does not claim self-awareness  
- does not claim intent  

It is a control architecture, not an agent.

---

## Responsibility Boundary

Responsibility remains with:

- system integrator  
- hardware designer  
- software implementer  
- operator  

AMNION-ORACLE provides architecture, not liability transfer.

---

## Misuse Prevention Principle

If AMNION-ORACLE is used outside defined scope:

- behavior is undefined  
- safety guarantees no longer apply  

Therefore:

**Scope violation = responsibility of integrator**

---

## Success Definition

A successful AMNION-ORACLE system is one that:

- avoids uncontrolled behavior  
- degrades gracefully  
- logs deterministically  
- fails safely  

Not one that “keeps running at all costs”.

---

## Summary

AMNION-ORACLE is:

A safety-oriented control architecture reference.

It is not:

A universal solution.  
A medical system.  
An autonomous intelligence.  
A security appliance.

Stability first.  
Safety first.  
Always.
