07_HARDWARE_SPEC — AMNION-ORACLE (Hardware Specification)

Project: AMNION-ORACLE  
Type: Hardware specification (concept-level)  
Scope: Sensor/actuator boundary + compute + power safety  
Status: Reference architecture (NOT clinical)

0. Non-medical / non-clinical disclaimer
AMNION-ORACLE is a concept-level engineering reference.
It is **NOT** a medical device and **NOT** intended for clinical use.


1. Hardware goals
- Predictable timing
- Stable power delivery
- Hardware-level safety caps
- Clean separation of sensing and actuation


2. Compute options
3. Option A — Host control
- Laptop / SBC
- USB/UART adapters
- Easiest for early validation

Option B — Microcontroller control
- MCU handles timing-critical loop
- Host used for monitoring/logging


3. Sensors (concept-level)
Required (minimum):
- phase/coherence measurement channel (abstract)
- power monitor (P_in, P_draw)
- temperature monitor (system stability)
- validity flags / watchdog

Policies:
- sensor timeout → guard degrade
- invalid data → clamp + barrier


4. Actuation (concept-level)
- control output channel (DAC/PWM abstract)
- throttle / limiter channel (optional)
- emergency stop / hard-disable

Rules:
- hard caps enforced at actuator boundary
- watchdog disables actuation if loop stalls


5. Power / safety interlocks
- max power clamp (hardware-level)
- fuse / breaker logic (concept)
- watchdog timer (WDT)
- brownout detection → safe shutdown


6. Connectivity
- UART / USB-serial for early prototypes
- Optional CAN/I2C/SPI for embedded sensors


7. Hardware logging support
- monotonic timestamp counter
- event marker channel
- ability to export minimal trace


8. Minimal validation checklist
- stable timing under load
- power clamp triggers correctly
- watchdog triggers correctly
- sensor timeout triggers degrade mode

 9. Resonant cell / capsule material (concept)

Target properties (engineering intent):
- mechanically stable under cyclic load
- electrically insulating base (where required)
- predictable piezoelectric transduction
- chemically inert / low-degradation carrier medium

Candidate material stack (concept-level reference):
- Frame / lattice: Ti-6Al-4V (or equivalent titanium alloy class)
- Piezo layer: AlN thin film (preferred for stability) OR PZT (higher response, higher complexity)
- Electrode layer: Au / Pt thin film (corrosion-resistant)
- Carrier medium: hydrogel / polymer gel class with stable viscosity window
- Optional barrier coat: biocompatible inert coating (concept), to reduce parasitic reactions

Design intent:
- material layer provides passive resonance + transduction (mechanical ↔ electrical)
- no active amplification at material level
- stability first: narrow-band response is allowed, runaway is not


10. Hardware-level envelopes (canonical)

These limits are enforced at the actuator boundary (hardware side),
even if software misbehaves.

10.1 Power envelope
- P_draw <= P_max_hw

10.2 Voltage envelope
- V_min <= V <= V_max

10.3 Current envelope
- I <= I_max

10.4 Thermal envelope
- T <= T_max

10.5 Actuator hard clamp (non-negotiable)
- u_hw = clamp(u_cmd, u_min, u_max)

Where:
- clamp(x, a, b) = min(max(x, a), b)

10.6 Watchdog rule
If the control loop misses ticks:
- if tick_miss > N_max -> HARD_DISABLE

10.7 Brownout rule
If supply collapses:
- if V < V_min -> SAFE_SHUTDOWN

10.8 Sensor timeout rule (hardware boundary)
If sensor stream stalls:
- if sensor_age_ms > sensor_timeout_ms -> DEGRADE_MODE
- if persistent stall -> HARD_DISABLE (actuation off)


11. Minimal validation checklist (hardware)

Pass conditions:
- stable timing under load (no tick drift beyond tolerance)
- P_max_hw clamp triggers deterministically
- watchdog triggers deterministically on stalled loop
- brownout triggers SAFE_SHUTDOWN
- sensor timeout triggers DEGRADE_MODE, and does not produce actuation spikes 
