# 13_THREAT_MODEL — AMNION-ORACLE (Threat Model)

**Project:** AMNION-ORACLE  
**Type:** Threat modeling & failure analysis (documentation-first)  
**Status:** Reference specification (NOT clinical)

---

## Non-medical / non-clinical disclaimer

AMNION-ORACLE is a concept-level engineering reference.  
It is NOT a medical device and NOT intended for clinical use.

---

## Purpose

Define what classes of threats, failures, and adversarial conditions AMNION-ORACLE is designed to withstand, detect, degrade under, or safely halt against.

This model covers:

- physical failures  
- signal-level attacks  
- software faults  
- configuration abuse  
- operator mistakes  
- environmental stressors  

**Primary principle:**  
The system assumes hostile or imperfect reality.  
No single layer is trusted.

---

## Threat model assumptions

- Sensors may lie, freeze, or disappear  
- Software may contain bugs  
- Operators may misconfigure parameters  
- Power may fluctuate  
- External signals may attempt to drive resonance into unstable regimes  

**Therefore:**  
Safety must emerge from physics + architecture, not policy.

---

## Threat categories

### T1 — Sensor-level threats

**Examples**

- missing frames  
- frozen values  
- stuck-at-zero / stuck-at-max  
- random noise injection  
- slow drift  

**Mitigations**

- sensor sanity checks  
- plausibility tests  
- derivative limits  
- sensor_valid flags  
- Guard escalation to THROTTLE or BARRIER  

**Outcome**

Invalid sensors must never propagate as valid state.

---

### T2 — Signal injection / resonance abuse

**Examples**

- forcing phase oscillation  
- external harmonic driving  
- attempting to push system into high-Q runaway  

**Mitigations**

- damping-first design  
- decoupling via Barrier  
- hardware envelopes  
- narrow-band acceptance  

**Outcome**

Unstable harmonics become energetically unfavorable.

---

### T3 — Power manipulation

**Examples**

- P_in collapse  
- P_draw spikes  
- brownout  
- supply noise  

**Mitigations**

- soft power throttle  
- P_max clamp  
- hardware-level caps  
- Guard power checks  

**Outcome**

Power violations lead to conservative behavior, never amplification.

---

### T4 — Software faults

**Examples**

- NaN / Inf propagation  
- overflow  
- division by zero  
- logic bug  

**Mitigations**

- clamp-safe outputs  
- deterministic defaults  
- Guard invariant checks  
- fail-closed behavior  

**Outcome**

Fault → degrade → barrier → halt.  
Never undefined actuation.

---

### T5 — Configuration abuse

**Examples**

- extreme gains  
- negative thresholds  
- mismatched units  

**Mitigations**

- config validation  
- bounded ranges  
- schema versioning  
- safe defaults  

**Outcome**

Invalid config blocks startup or forces SAFE mode.

---

### T6 — Operator error

**Examples**

- wrong mode selection  
- wrong parameter file  
- hot reload at wrong time  

**Mitigations**

- Guard dominance  
- monotonic safety logic  
- manual restart required after SAFE_HALT  

**Outcome**

Human cannot override safety invariants.

---

### T7 — Logging / audit tampering

**Examples**

- deleting logs  
- modifying traces  
- partial capture  

**Mitigations**

- append-only logs  
- hash manifests  
- optional hash chaining  

**Outcome**

Tampering becomes detectable.

---

### T8 — Environmental stress

**Examples**

- temperature extremes  
- vibration  
- EMI  

**Mitigations**

- hardware envelopes  
- derating rules  
- Guard-driven damping and throttling  

**Outcome**

System reduces performance before damage.

---

## Threats explicitly out of scope

- Military-grade cryptographic adversaries  
- Physical destruction of hardware  
- Nation-state supply-chain attacks  

**Rationale**

AMNION-ORACLE is a safety architecture, not a hardened security appliance.

---

## Failure handling philosophy

Any ambiguity → conservative behavior.

**Priority order**

1. THROTTLE  
2. BARRIER  
3. SAFE_HALT  

Never attempt to “power through” uncertainty.

---

## Success condition

A successful defense is **not** continued operation at any cost.

But:

- No uncontrolled actuation  
- No runaway energy  
- No silent corruption  

**Graceful degradation is success.**
