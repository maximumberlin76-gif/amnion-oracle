# controller/lawx_adapter.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class LawXResult:
    mode: str = "ALLOW"               # ALLOW / THROTTLE / ISOLATE / DEGRADE
    confidence: float = 0.0
    pattern: str = "CLEAN"
    attack_signature: str = ""
    state_l0: str = "OK"              # OK / WARN / ISOLATE / LOCK
    q_est: float = 0.0
    r_order: float = 0.0
    phase_mismatch: float = 0.0
    power_noise: float = 0.0
    gap: float = 0.0
    p_draw: float = 0.0


class LawXAdapter:
    """
    Adapter around LawX full stack (SingularConscienceEngine).
    - deterministic per input frame (assuming engine is deterministic)
    - must never throw
    - if LawX module is not present, becomes a no-op returning default ALLOW
    """

    def __init__(self, enabled: bool = True):
        self.enabled = bool(enabled)
        self._engine = None
        self._SensorFrame = None

        if not self.enabled:
            return

        # Lazy import: if you didn't place lawx_full_stack.py into controller/, adapter degrades to no-op.
        try:
            from controller.lawx_full_stack import SingularConscienceEngine, SensorFrame  # type: ignore
            self._engine = SingularConscienceEngine()
            self._SensorFrame = SensorFrame
        except Exception:
            self._engine = None
            self._SensorFrame = None

    def _extract_frame(self, sensors: Dict[str, Any]) -> Optional[object]:
        """
        Map controller sensors → LawX SensorFrame.
        Expected (best-effort):
            pattern: array-like (list[float] / numpy array)
            reported_growth: float
            energy_input: float
        """
        if self._SensorFrame is None:
            return None

        pattern = sensors.get("pattern", None)
        reported_growth = sensors.get("reported_growth", None)
        energy_input = sensors.get("energy_input", None)

        # Hard requirement for LawX to run meaningfully
        if pattern is None or reported_growth is None or energy_input is None:
            return None

        try:
            return self._SensorFrame(pattern=pattern, reported_growth=float(reported_growth), energy_input=float(energy_input), ts=float(sensors.get("ts", 0.0)))  # type: ignore
        except Exception:
            return None

    def process(self, sensors: Dict[str, Any]) -> LawXResult:
        """
        Run LawX engine on current frame.
        Must never throw; returns ALLOW if unavailable.
        """
        if not self.enabled or self._engine is None:
            return LawXResult()

        frame = self._extract_frame(sensors)
        if frame is None:
            return LawXResult()

        try:
            p_out, diag = self._engine.process(frame)  # diag is GuardDiag from lawx_full_stack
        except Exception:
            return LawXResult()

        # Map diag fields (keep it stable and explicit)
        try:
            return LawXResult(
                mode=str(getattr(diag, "mode_l1", "ALLOW")),
                confidence=float(getattr(diag, "law_x_confidence", 0.0)),
                pattern=str(getattr(diag, "law_x_pattern", "CLEAN")),
                attack_signature=str(getattr(diag, "attack_signature", "")),
                state_l0=str(getattr(diag, "state", "OK")),
                q_est=float(getattr(diag, "q_est", 0.0)),
                r_order=float(getattr(diag, "r_order", 0.0)),
                phase_mismatch=float(getattr(diag, "phase_mismatch", 0.0)),
                power_noise=float(getattr(diag, "power_noise", 0.0)),
                gap=float(getattr(diag, "gap", 0.0)),
                p_draw=float(getattr(diag, "p_draw", float(p_out or 0.0))),
            )
        except Exception:
            return LawXResult()

      
