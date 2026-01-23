# controller/safety_gate.py
# Safety gating for AMNION–ORACLE (prototype skeleton).
# English-only repo: keep code/comments in English.

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class SafetyGate:
    """
    Minimal safety gate.
    Returns a decision dict:
      {"allow": bool, "reasons": [str, ...], "limits": {...}}
    """

    min_coherence: float = 0.80
    max_temperature: float = 39.0
    max_pressure: float = 2.0

    def evaluate(self, obs: Dict[str, Any]) -> Dict[str, Any]:
        reasons: List[str] = []

        temperature = _to_float(obs.get("temperature"))
        pressure = _to_float(obs.get("pressure"))
        coherence = _to_float(obs.get("coherence"))
        emergency_stop = bool(obs.get("emergency_stop", False))

        if emergency_stop:
            reasons.append("emergency_stop=true")

        if coherence is None:
            reasons.append("missing:coherence")
        elif coherence < self.min_coherence:
            reasons.append(f"coherence<{self.min_coherence:.2f}")

        if temperature is None:
            reasons.append("missing:temperature")
        elif temperature > self.max_temperature:
            reasons.append(f"temperature>{self.max_temperature:.1f}")

        if pressure is None:
            reasons.append("missing:pressure")
        elif pressure > self.max_pressure:
            reasons.append(f"pressure>{self.max_pressure:.2f}")

        allow = len(reasons) == 0
        return {
            "allow": allow,
            "reasons": reasons,
            "limits": {
                "min_coherence": self.min_coherence,
                "max_temperature": self.max_temperature,
                "max_pressure": self.max_pressure,
            },
        }


def _to_float(x: Any) -> Optional[float]:
    if x is None:
        return None
    try:
        return float(x)
    except (TypeError, ValueError):
        return None
