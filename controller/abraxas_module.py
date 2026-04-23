# controller/abraxas_module.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List


@dataclass
class AbraxasDiag:
    f_ref: float = 0.0
    f_tol: float = 0.0
    phase_error: float = 0.0
    loop_closure: bool = False
    state_integrity: float = 0.0
    integrity_min: float = 0.0
    violations: List[str] = None  # filled in factory

    def __post_init__(self):
        if self.violations is None:
            self.violations = []


class AbraxasModule:
    """
    ABRAXAS-764 invariants checker.
    Deterministic, pure evaluation. No side effects. Never throws.

    Invariants (from docs):
      I6: |f_ref - 76.4| <= f_tol
      I7: loop_closure == True
      I8: state_integrity >= integrity_min
    """

    def __init__(
        self,
        f_ref_default: float = 76.4,
        f_tol_default: float = 0.5,
        integrity_min_default: float = 0.73,
    ):
        self.f_ref_default = float(f_ref_default)
        self.f_tol_default = float(f_tol_default)
        self.integrity_min_default = float(integrity_min_default)

    def evaluate(self, sensors: Dict[str, Any]) -> AbraxasDiag:
        """
        Best-effort extraction:
          - f_ref: sensors['f_ref'] or sensors['mark_hz'] or default 76.4
          - phase_error: sensors['phase_error'] or sensors['phase_noise'] or 0.0
          - loop_closure: sensors['loop_closure'] bool-ish
          - state_integrity: sensors['state_integrity'] or sensors['sensor_health'] or 0.0
          - tolerances: sensors['f_tol'], sensors['integrity_min'] optional
        """
        try:
            f_ref = float(sensors.get("f_ref", sensors.get("mark_hz", self.f_ref_default)))
        except Exception:
            f_ref = self.f_ref_default

        try:
            f_tol = float(sensors.get("f_tol", self.f_tol_default))
        except Exception:
            f_tol = self.f_tol_default

        try:
            phase_error = float(sensors.get("phase_error", sensors.get("phase_noise", 0.0)))
        except Exception:
            phase_error = 0.0

        lc_raw = sensors.get("loop_closure", False)
        loop_closure = bool(lc_raw) if not isinstance(lc_raw, str) else (lc_raw.strip().lower() in ("1", "true", "yes", "y", "on"))

        try:
            state_integrity = float(sensors.get("state_integrity", sensors.get("sensor_health", 0.0)))
        except Exception:
            state_integrity = 0.0

        try:
            integrity_min = float(sensors.get("integrity_min", self.integrity_min_default))
        except Exception:
            integrity_min = self.integrity_min_default

        violations: List[str] = []

        # I6
        if abs(f_ref - 76.4) > f_tol:
            violations.append("I6_RESONANCE_LOCK")

        # I7
        if not loop_closure:
            violations.append("I7_LOOP_CLOSURE")

        # I8
        if state_integrity < integrity_min:
            violations.append("I8_STATE_INTEGRITY")

        return AbraxasDiag(
            f_ref=f_ref,
            f_tol=f_tol,
            phase_error=phase_error,
            loop_closure=loop_closure,
            state_integrity=state_integrity,
            integrity_min=integrity_min,
            violations=violations,
        )

