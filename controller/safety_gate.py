# controller/safety_gate.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class SafetyState:
    allowed: bool
    reason: str = ""
    power_budget: float | None = None
    notes: Dict[str, Any] | None = None


class SafetyGate:
    """
    SafetyGate:
      - sanitize_inputs(): lightweight input normalization
      - evaluate(): decision "allowed/blocked" + optional limits (e.g. power_budget)

    Expected cfg structure (example):
      safety:
        coherence_min: 0.2
        phase_jump_max: 3.2
        power_budget_w: 800.0
        hard_block:
          - if: "coherence < 0.05"
            reason: "coherence_too_low"
    """

    def __init__(self, cfg: Dict[str, Any], log):
        self.cfg = cfg or {}
        self.log = log

        self.coherence_min = float(self.cfg.get("coherence_min", 0.0))
        self.phase_jump_max = float(self.cfg.get("phase_jump_max", 999.0))
        self.power_budget_w = self.cfg.get("power_budget_w", None)

    def sanitize_inputs(self, sensors: Dict[str, Any]) -> Dict[str, Any]:
        if sensors is None:
            return {}

        safe: Dict[str, Any] = dict(sensors)

        # best-effort numeric coercions
        for k in ("phase", "coherence", "power_in", "power_draw"):
            if k in safe:
                try:
                    safe[k] = float(safe[k])
                except Exception:
                    safe.pop(k, None)

        # clamp coherence into [0, 1]
        if "coherence" in safe:
            c = safe["coherence"]
            if c < 0.0:
                safe["coherence"] = 0.0
            elif c > 1.0:
                safe["coherence"] = 1.0

        return safe

    def evaluate(self, safe_sensors: Dict[str, Any]) -> Dict[str, Any]:
        """
        Returns a serializable dict:
          { "allowed": bool, "reason": str, "power_budget": float|None, "notes": {...} }
        """
        notes: Dict[str, Any] = {}

        coherence = float(safe_sensors.get("coherence", 1.0) or 0.0)
        phase = float(safe_sensors.get("phase", 0.0) or 0.0)

        # basic coherence gate
        if coherence < self.coherence_min:
            return {
                "allowed": False,
                "reason": "coherence_below_min",
                "power_budget": None,
                "notes": {"coherence": coherence, "min": self.coherence_min},
            }

        # power budget limit
        power_budget = None
        if self.power_budget_w is not None:
            try:
                power_budget = float(self.power_budget_w)
            except Exception:
                power_budget = None

        # optional hard-block rules (no code execution, only known patterns)
        hard = self.cfg.get("hard_block", []) or []
        for rule in hard:
            try:
                cond = str(rule.get("if", "")).strip()
                reason = str(rule.get("reason", "blocked")).strip()

                if cond == "coherence < 0.05" and coherence < 0.05:
                    return {
                        "allowed": False,
                        "reason": reason,
                        "power_budget": None,
                        "notes": {"coherence": coherence},
                    }

                if cond == "power_draw > power_in":
                    power_draw = float(safe_sensors.get("power_draw", 0.0) or 0.0)
                    power_in = float(safe_sensors.get("power_in", 0.0) or 0.0)
                    if power_draw > power_in:
                        return {
                            "allowed": False,
                            "reason": reason,
                            "power_budget": power_budget,
                            "notes": {"power_draw": power_draw, "power_in": power_in},
                        }
            except Exception:
                continue

        notes["coherence"] = coherence
        notes["phase"] = phase

        return {
            "allowed": True,
            "reason": "",
            "power_budget": power_budget,
            "notes": notes,
        }
      
