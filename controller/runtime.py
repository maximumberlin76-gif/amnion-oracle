# controller/runtime.py
# Runtime execution for AMNION-ORACLE (documentation-first).
# Applies SafetyGate decision to produce final actuator command.

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional


def _to_float(x: Any) -> Optional[float]:
    if x is None:
        return None
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))


@dataclass
class RuntimeConfig:
    # Canonical limits (runtime is independent)
    P_max: float = 1.0
    u_min: float = 0.0
    u_max: float = 1.0

    # Default control coefficients
    G_default: float = 1.0
    K_default: float = 1.0
    D_default: float = 0.1

    # Barrier numeric mapping
    D_high_value: float = 1.0

    # Minimal safe output when SAFE_HALT
    u_safe_halt: float = 0.0


@dataclass
class Runtime:
    cfg: RuntimeConfig = field(default_factory=RuntimeConfig)

    def compute(self, sensors: Dict[str, Any], safety_state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Produce final control_frame after applying safety patch.

        sensors (concept-level):
          - desired_u (optional) or P_draw_request (optional)
          - G, K, D (optional)

        safety_state:
          - state, allow_control, patch{...}, limits{...}
        """
        sensors = sensors or {}
        safety_state = safety_state or {}

        patch = safety_state.get("patch") or {}
        state = str(safety_state.get("state", "S0_NORMAL"))
        allow_control = bool(safety_state.get("allow_control", True))

        limits = safety_state.get("limits") or {}
        P_max = _to_float(limits.get("P_max")) or self.cfg.P_max
        P_budget_min = _to_float(limits.get("P_budget_min"))
        if P_budget_min is None:
            P_budget_min = 0.0
        P_budget_soft = _to_float(limits.get("P_budget_soft"))
        if P_budget_soft is None:
            P_budget_soft = min(P_max, 0.8)

        # --- Proposed control request ---
        desired_u = _to_float(sensors.get("desired_u"))
        if desired_u is None:
            desired_u = _to_float(sensors.get("P_draw_request"))
        if desired_u is None:
            desired_u = 0.0

        # Always clamp to actuator envelope first
        desired_u = clamp(desired_u, self.cfg.u_min, self.cfg.u_max)

        # Proposed params (optional)
        G = _to_float(sensors.get("G")) or self.cfg.G_default
        K = _to_float(sensors.get("K")) or self.cfg.K_default
        D = _to_float(sensors.get("D")) or self.cfg.D_default

        mode = str(patch.get("mode", "NONE")).upper()

        # SAFE_HALT
        if mode == "SAFE_HALT" or state == "S3_SAFE_HALT":
            return {
                "state": "SAFE_HALT",
                "u_cmd": self.cfg.u_safe_halt,
                "G": 0.0,
                "K": 0.0,
                "D": self._map_D(patch.get("D", "HIGH")),
                "P_budget": 0.0,
                "notes": ["safe_halt"],
            }

        # If guard disallows control, force BARRIER deterministically
        if not allow_control:
            mode = "BARRIER"

        # BARRIER
        if mode == "BARRIER" or state == "S2_BARRIER":
            K = 0.0
            D = self._map_D(patch.get("D", "HIGH"))

            P_budget = _to_float(patch.get("P_budget"))
            if P_budget is None:
                P_budget = P_budget_min

            u_cap = min(P_max, P_budget)
            u_cmd = clamp(desired_u, 0.0, u_cap)
            u_cmd = clamp(u_cmd, self.cfg.u_min, self.cfg.u_max)

            notes = ["barrier"]
            if patch.get("freeze_fast_adaptation"):
                notes.append("freeze_fast_adaptation")

            return {
                "state": "BARRIER",
                "u_cmd": u_cmd,
                "G": 0.0,
                "K": K,
                "D": D,
                "P_budget": P_budget,
                "notes": notes,
            }

        # THROTTLE
        if mode == "THROTTLE" or state == "S1_THROTTLE":
            G_scale = _to_float(patch.get("G_scale")) or 1.0
            K_scale = _to_float(patch.get("K_scale")) or 1.0
            D_boost = _to_float(patch.get("D_boost")) or 1.0

            P_budget = _to_float(patch.get("P_budget"))
            if P_budget is None:
                P_budget = P_budget_soft

            G = max(0.0, G * G_scale)
            K = max(0.0, K * K_scale)
            D = max(0.0, D * D_boost)

            u_cap = min(P_max, P_budget)
            u_cmd = clamp(desired_u, 0.0, u_cap)
            u_cmd = clamp(u_cmd, self.cfg.u_min, self.cfg.u_max)

            return {
                "state": "THROTTLE",
                "u_cmd": u_cmd,
                "G": G,
                "K": K,
                "D": D,
                "P_budget": P_budget,
                "notes": ["throttle"],
            }

        # NORMAL
        u_cmd = clamp(desired_u, 0.0, P_max)
        u_cmd = clamp(u_cmd, self.cfg.u_min, self.cfg.u_max)

        return {
            "state": "NORMAL",
            "u_cmd": u_cmd,
            "G": G,
            "K": K,
            "D": D,
            "P_budget": P_max,
            "notes": ["normal"],
        }

    def _map_D(self, d_value: Any) -> float:
        if isinstance(d_value, (int, float)):
            return float(d_value)
        s = str(d_value).upper()
        if s == "HIGH":
            return self.cfg.D_high_value
        if s == "LOW":
            return self.cfg.D_default
        return self.cfg.D_high_value
