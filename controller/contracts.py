# controller/contracts.py
# Deterministic interface contracts between controller and hardware

from __future__ import annotations
from dataclasses import dataclass
from typing import Optional


# =========================
# Sensor Frame (input)
# =========================
@dataclass
class SensorFrame:
    P_in: Optional[float] = None
    P_draw: Optional[float] = None
    Q: Optional[float] = None
    phase_error: Optional[float] = None
    temp_c: Optional[float] = None
    sensor_valid: bool = True


# =========================
# Derived Metrics
# =========================
@dataclass
class DerivedMetrics:
    mismatch_power: Optional[float] = None
    mismatch_phase: Optional[float] = None
    coherence_score: float = 0.0


# =========================
# Safety State
# =========================
@dataclass
class SafetyState:
    state: str = "S0_NORMAL"
    allow_control: bool = True
    P_budget: float = 0.0


# =========================
# Control Output
# =========================
@dataclass
class ControlOutput:
    u_control: float = 0.0
    mode: str = "NORMAL"
    P_budget: float = 0.0


# =========================
# Clamp utility
# =========================
def clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))
