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
  
