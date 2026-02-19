07_HARDWARE_SPEC — AMNION-ORACLE (Hardware Specification)

Project: AMNION-ORACLE  
Type: Hardware specification (concept-level)  
Scope: Sensor/actuator boundary + compute + power safety  
Status: Reference architecture (NOT clinical)

0. Non-medical / non-clinical disclaimer
AMNION-ORACLE is a concept-level engineering reference.
It is NOT a medical device and NOT intended for clinical use.


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

Sensor → Metric Mapping (reference)

Temp sensor        → temp_c
Power monitor      → power_w / P_draw
Phase channel      → phase_noise / q_factor proxy
Watchdog validity  → sensor_health

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

Materials listed below are engineering-class examples for structural discussion only.
No fabrication instructions are provided in this repository.

 9. Resonant cell / capsule material (concept)

Target properties (engineering intent):
- mechanically stable under cyclic load
- electrically insulating base (where required)
- predictable piezoelectric transduction
- chemically inert / low-degradation carrier medium

Candidate material stack (concept-level reference):

Recommended polling ranges 

temperature: 1–10 Hz
power monitor: 50–200 Hz
phase/coherence: 500–2000 Hz
watchdog: >= control loop rate

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


Mode        Power budget intent
Nominal     <= P_budget_nominal
Throttle    reduced duty cycle
Degraded    minimal safe consumption
Lock        actuation off

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

11.1 Mechanical load envelope (structural)

Goal:
Prevent mechanical fatigue, plastic deformation, or resonance-induced fracture.

Definitions:
- σ — applied stress
- σ_yield — yield strength of frame material
- σ_fatigue — fatigue limit (for cyclic load)
- N_cycles — expected number of cycles

Constraints:

- σ <= 0.5 * σ_yield
- σ <= σ_fatigue

For cyclic loading:

- Damage accumulation must satisfy:
  Σ (n_i / N_i) < 1.0   (Miner’s rule)

Where:
- n_i = applied cycles at load level i  
- N_i = allowable cycles at load level i  

Design intent:
- operate in elastic region only
- no plastic deformation in normal or fault conditions

Monitoring:

- estimate stress proxy from actuator command and geometry
- if estimated σ approaches limit -> reduce gain (G ↓) and damping (D ↑)


11.2 Resonant constraints (hardware-level)

Goal:
Avoid resonance runaway and destructive standing waves.

Definitions:
- f0 — nominal resonance frequency
- Δf — deviation from f0
- Q_hw — hardware resonance quality factor
- Q_hw_max — maximum allowed hardware Q
- A — oscillation amplitude
- A_max — maximum safe amplitude

Constraints:

- |Δf| <= Δf_max_hw
- Q_hw <= Q_hw_max
- A <= A_max

Soft protection:

- if |Δf| > 0.7 * Δf_max_hw:
    reduce gain (G ↓)
    increase damping (D ↑)

Hard protection:

- if |Δf| > Δf_max_hw:
    HARD_DISABLE

- if A > A_max:
    HARD_DISABLE

Design intent:
- hardware never amplifies outside narrow safe band
- unstable harmonics are physically suppressed

Notes:

- hardware resonance is treated as a filter, not an amplifier
- amplification happens only in controlled software layer 
