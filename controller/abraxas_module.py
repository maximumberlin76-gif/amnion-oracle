# controller/abraxas_module.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional


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
            phase_error = float(sensors.get("phase_error", sensors.get("phase_noise",

                                                                       
