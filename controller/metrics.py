# controller/metrics.py
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


def _to_float(x: Any) -> Optional[float]:
    if x is None:
        return None
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


@dataclass
class MetricsConfig:
    enabled: bool = True
    max_history: int = 512


@dataclass
class Metrics:
    """
    Lightweight runtime metrics collector.

    Compatibility:
      - update(sensors, safety_state, output)
      - on_tick(sensors, safety_state, output)  # alias
    """

    cfg: MetricsConfig = field(default_factory=MetricsConfig)
    log: Any = None

    ticks: int = 0
    violations: int = 0
    last: Dict[str, Any] = field(default_factory=dict)
    history: List[Dict[str, Any]] = field(default_factory=list)

    def update(
        self,
        sensors: Dict[str, Any],
        safety_state: Dict[str, Any],
        output: Dict[str, Any],
    ) -> None:
        if not self.cfg.enabled:
            return

        sensors = sensors or {}
        safety_state = safety_state or {}
        output = output or {}

        self.ticks += 1

        # Accept both styles:
        # - safety_state["ok"] boolean
        # - allow_control + state fallback
        ok = safety_state.get("ok")
        if ok is None:
            allow_control = bool(safety_state.get("allow_control", True))
            state = str(safety_state.get("state", "S0_NORMAL"))
            ok = allow_control and (state not in ("S2_BARRIER", "S3_SAFE_HALT"))

        if not bool(ok):
            self.violations += 1

        # Normalize common sensor names (support both old/new keys)
        coherence = sensors.get("coherence")
        phase = sensors.get("phase")
        power_in = sensors.get("power_in", sensors.get("P_in"))
        power_draw = sensors.get("power_draw", sensors.get("P_draw"))

        summary = {
            "tick": self.ticks,
            "ok": bool(ok),
            "violations_total": self.violations,
            "state": safety_state.get("state"),
            "allow_control": safety_state.get("allow_control"),
            "coherence": _to_float(coherence) if coherence is not None else coherence,
            "phase": _to_float(phase) if phase is not None else phase,
            "power_in": _to_float(power_in) if power_in is not None else power_in,
            "power_draw": _to_float(power_draw) if power_draw is not None else power_draw,
            "mismatch_power": safety_state.get("mismatch_power"),
            "mismatch_phase": safety_state.get("mismatch_phase"),
            "flags": list(safety_state.get("flags", [])) if safety_state.get("flags") is not None else [],
            "u_cmd": output.get("u_cmd"),
            "G": output.get("G"),
            "K": output.get("K"),
            "D": output.get("D"),
            "P_budget": output.get("P_budget"),
        }

        self.last = summary
        self.history.append(summary)

        if len(self.history) > self.cfg.max_history:
            self.history = self.history[-self.cfg.max_history :]

        if self.log:
            try:
                self.log.debug(f"metrics tick={self.ticks} ok={bool(ok)} violations={self.violations}")
            except Exception:
                pass

    # Alias for older controller code (so nothing breaks)
    def on_tick(
        self,
        sensors: Dict[str, Any],
        safety_state: Dict[str, Any],
        output: Dict[str, Any],
    ) -> None:
        self.update(sensors, safety_state, output)

    def snapshot(self) -> Dict[str, Any]:
        return {
            "enabled": self.cfg.enabled,
            "ticks": self.ticks,
            "violations": self.violations,
            "last": self.last,
        }

    def get_history(self, n: Optional[int] = None) -> List[Dict[str, Any]]:
        if n is None:
            return list(self.history)
        n = max(0, int(n))
        if n == 0:
            return []
        return self.history[-n:]
