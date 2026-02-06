# controller/metrics.py
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class Metrics:
    """
    Lightweight runtime metrics collector.
    Stores last tick summary + history (bounded).
    """
    cfg: Dict[str, Any]
    log: Any = None

    enabled: bool = True
    max_history: int = 512

    ticks: int = 0
    violations: int = 0
    last: Dict[str, Any] = field(default_factory=dict)
    history: List[Dict[str, Any]] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.enabled = bool(self.cfg.get("enabled", True))
        self.max_history = int(self.cfg.get("max_history", self.max_history))

    def on_tick(
        self,
        sensors: Dict[str, Any],
        safety_state: Dict[str, Any],
        output: Dict[str, Any],
    ) -> None:
        if not self.enabled:
            return

        self.ticks += 1

        ok = bool(safety_state.get("ok", True))
        if not ok:
            self.violations += 1

        summary = {
            "tick": self.ticks,
            "ok": ok,
            "violations_total": self.violations,
            "coherence": sensors.get("coherence"),
            "phase": sensors.get("phase"),
            "power_in": sensors.get("power_in"),
            "power_draw": sensors.get("power_draw"),
            "mismatch_power": safety_state.get("mismatch_power"),
            "mismatch_phase": safety_state.get("mismatch_phase"),
            "output": output,
            "flags": list(safety_state.get("flags", [])),
        }

        self.last = summary
        self.history.append(summary)
        if len(self.history) > self.max_history:
            self.history = self.history[-self.max_history :]

        if self.log:
            # keep logging minimal and machine-readable
            try:
                self.log.debug(f"metrics.tick={self.ticks} ok={ok} violations={self.violations}")
            except Exception:
                pass

    def snapshot(self) -> Dict[str, Any]:
        return {
            "enabled": self.enabled,
            "ticks": self.ticks,
            "violations": self.violations,
            "last": self.last,
        }

    def get_history(self, n: Optional[int] = None) -> List[Dict[str, Any]]:
        if n is None:
            return list(self.history)
        n = max(0, int(n))
        return sel
        f.history[-n:]
