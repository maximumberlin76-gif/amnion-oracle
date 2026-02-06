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
    # Canonical limits (should match SafetyConfig defaults, but runtime is independent)
    P_max: float = 1.0
    u_min: float = 0.0
    u_max: float = 1.0

    # Default control coefficients (used when sensors do not provide suggested values)
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

        Inputs expected (concept-level):
          sensors:
            - P_in (optional)
            - P_draw (optional)
            - desired_u (optional)  # proposed actuation request from upstream controller
            - G, K, D (optional)    # proposed parameters
          safety_state:
            - state, allow_control, patch{...}, limits{...}

        Output:
          control_frame dict with bounded 'u_cmd' and applied parameters.
        """
        sensors = sensors or {}
        safety_state = safety_state or {}

        patch = safety_state.get("patch") or {}
        state = str(safety_state.get("state", "S0_NORMAL"))
        allow_control = bool(safety_state.get("allow_control", True))

        # Pull limits from safety if present, else runtime defaults
        limits = safety_state.get("limits") or {}
        P_max = _to_float(limits.get("P_max")) or self.cfg.P_max

        # --- Proposed control request (from upstream controller) ---
        # If nothing given, default to 0 for safety.
        desired_u = _to_float(sensors.get("desired_u"))
        if desired_u is None:
            # Fallback: if user gives "P_draw_request" treat as desired_u
            desired_u = _to_float(sensors.get("P_draw_request"))
        if desired_u is None:
            desired_u = 0.0

        # Clamp desired u to runtime actuator envelope first (always)
        desired_u = clamp(desired_u, self.cfg.u_min, self.cfg.u_max)

        # Proposed params (optional)
        G = _to_float(sensors.get("G")) or self.cfg.G_default
        K = _to_float(sensors.get("K")) or self.cfg.K_default
        D = _to_float(sensors.get("D")) or self.cfg.D_default

        # --- Apply patch modes ---
        mode = str(patch.get("mode", "NONE")).upper()

        if mode == "SAFE_HALT" or state == "S3_SAFE_HALT":
            # Absolute stop. No actuation.
            return {
                "state": "SAFE_HALT",
                "u_cmd": self.cfg.u_safe_halt,
                "G": 0.0,
                "K": 0.0,
                "D": self._map_D(patch.get("D", "HIGH")),
                "P_budget": 0.0,
                "notes": ["safe_halt"],
            }

        # If guard disallows control, we still produce a safe command (0 or capped) deterministically
        if not allow_control:
            # Barrier is the canonical response.
            mode = "BARRIER"

        if mode == "BARRIER" or state == "S2_BARRIER":
            # decouple + damp + cap
            K = 0.0
            D = self._map_D(patch.get("D", "HIGH"))
            P_budget = _to_float(patch.get("P_budget"))
            if P_budget is None:
                # If safety did not supply, use small cap
                P_budget = 0.0
            # u_cmd is capped by P_budget AND hard P_max AND actuator envelope
            u_cmd = clamp(desired_u, 0.0, min(P_max, P_budget))
            u_cmd = clamp(u_cmd, self.cfg.u_min, self.cfg.u_max)

            notes = ["barrier"]
            if patch.get("freeze_fast_adaptation"):
                notes.append("freeze_fast_adaptation")

            return {
                "state": "BARRIER",
                "u_cmd": u_cmd,
                "G": 0.0,          # in barrier: gain effectively off
                "K": K,
                "D": D,
                "P_budget": P_budget,
                "notes": notes,
            }

        if mode == "THROTTLE" or state == "S1_THROTTLE":
            # soft conservative limitation
            G_scale = _to_float(patch.get("G_scale")) or 1.0
            K_scale = _to_float(patch.get("K_scale")) or 1.0
            D_boost = _to_float(patch.get("D_boost")) or 1.0
            P_budget = _to_float(patch.get("P_budget"))
            if P_budget is None:
                P_budget = P_max

            G = max(0.0, G * G_scale)
            K = max(0.0, K * K_scale)
            D = max(0.0, D * D_boost)

            # u_cmd capped softly by P_budget and P_max
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
        # Still clamp by P_max (hard) and actuator envelope.
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
        """
        Map symbolic damping requests to numeric.
        """
        if isinstance(d_value, (int, float)):
            return float(d_value)
        s = str(d_value).upper()
        if s == "HIGH":
            return self.cfg.D_high_value
        if s == "LOW":
            return self.cfg.D_default
        return self.cfg.D_high_value
