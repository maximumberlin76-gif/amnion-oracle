# controller/runtime.py
# Deterministic runtime for AMNION-ORACLE
# No clinical use. No direct hardware actuation.

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional


def clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))


@dataclass
class RuntimeConfig:
    # Control output bounds
    u_min: float = 0.0
    u_max: float = 1.0

    # Default nominal control
    u_nominal: float = 0.5

    # Default budgets
    P_budget_nominal: float = 0.8
    P_budget_min: float = 0.0

    # Safety fallback
    fail_safe_u: float = 0.0


@dataclass
class Runtime:
    cfg: RuntimeConfig = field(default_factory=RuntimeConfig)

    def compute(self, sensors: Dict[str, Any], safety_state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Deterministic runtime step.

        Inputs:
            sensors: sanitized + enriched sensor dict
            safety_state: output of SafetyGate.evaluate()

        Output:
            {
                "u_control": float,
                "mode": str,
                "P_budget": float,
            }
        """

        sensors = sensors or {}
        safety_state = safety_state or {}

        patch = safety_state.get("patch", {}) or {}
        state = str(safety_state.get("state", "S0_NORMAL"))
        allow_control = bool(safety_state.get("allow_control", True))

        # ------------------------------------------------------------
        # 1) Read base metrics
        # ------------------------------------------------------------
        q = self._to_float(sensors.get("Q"))
        coherence = self._to_float(sensors.get("coherence_score"))
        rate_change = self._to_float(sensors.get("rate_change"))
        phase_error = self._to_float(sensors.get("phase_error"))
        p_draw = self._to_float(sensors.get("P_draw"))

        # ------------------------------------------------------------
        # 2) Base nominal control
        # ------------------------------------------------------------
        u = self.cfg.u_nominal

        # Prefer coherence / Q if available
        if q is not None:
            u *= clamp(q, 0.0, 1.0)
        elif coherence is not None:
            u *= clamp(coherence, 0.0, 1.0)

        # Penalize phase instability
        if phase_error is not None:
            u *= clamp(1.0 - abs(phase_error), 0.0, 1.0)

        # Penalize rapid change
        if rate_change is not None:
            penalty = clamp(1.0 - min(abs(rate_change), 1.0), 0.0, 1.0)
            u *= penalty

        # ------------------------------------------------------------
        # 3) Apply patch from SafetyGate
        # ------------------------------------------------------------
        mode = str(patch.get("mode", "NONE"))
        p_budget = self._to_float(patch.get("P_budget"))
        if p_budget is None:
            p_budget = self.cfg.P_budget_nominal

        if mode == "THROTTLE":
            g_scale = self._to_float(patch.get("G_scale")) or 1.0
            u *= g_scale

        elif mode == "BARRIER":
            u = self.cfg.fail_safe_u
            p_budget = self.cfg.P_budget_min

        elif mode == "SAFE_HALT":
            u = 0.0
            p_budget = 0.0

        # ------------------------------------------------------------
        # 4) Respect allow_control flag
        # ------------------------------------------------------------
        if not allow_control:
            u = 0.0

        # ------------------------------------------------------------
        # 5) Clamp output
        # ------------------------------------------------------------
        u = clamp(u, self.cfg.u_min, self.cfg.u_max)

        # ------------------------------------------------------------
        # 6) Normalize outward mode naming
        # ------------------------------------------------------------
        outward_mode = self._map_state_to_mode(state, mode)

        return {
            "u_control": u,
            "mode": outward_mode,
            "P_budget": p_budget,
        }

    @staticmethod
    def _to_float(x: Any) -> Optional[float]:
        try:
            return None if x is None else float(x)
        except Exception:
            return None

    @staticmethod
    def _map_state_to_mode(state: str, patch_mode: str) -> str:
        if state == "S3_SAFE_HALT":
            return "LOCK"
        if state == "S2_BARRIER":
            return "BARRIER"
        if state == "S1_THROTTLE":
            return "THROTTLE"
        if patch_mode == "SAFE_HALT":
            return "LOCK"
        if patch_mode == "BARRIER":
            return "BARRIER"
        if patch_mode == "THROTTLE":
            return "THROTTLE"
        return "NORMAL"
