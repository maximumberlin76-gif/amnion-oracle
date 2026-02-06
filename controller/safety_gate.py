# controller/safety_gate.py
# Safety gate for AMNION-ORACLE (documentation-first).
# Implements: sanitize_inputs() + evaluate() with monotonic safety behavior.

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple


def _to_float(x: Any) -> Optional[float]:
    if x is None:
        return None
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def _clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))


@dataclass
class SafetyConfig:
    # --- Canonical safety limits ---
    P_max: float = 1.0
    P_budget_min: float = 0.1
    P_budget_soft: float = 0.7

    # --- Trips / thresholds ---
    Q_crit: float = 0.50
    phase_trip: float = 0.50     # rad
    rate_trip: float = 1.00      # units/tick (hard trip)
    rate_limit: float = 0.30     # units/tick (soft throttle)

    # --- Sensor sanity ---
    sensor_timeout_ticks: int = 5  # optional use in runtime
    require_fields: Tuple[str, ...] = ("P_draw", "Q", "phase_error", "rate_change")

    # --- Basic ranges (optional sanity) ---
    Q_min: float = 0.0
    Q_max: float = 1.0


@dataclass
class SafetyGate:
    """
    Returns safety_state dict for runtime:
      {
        "state": "S0_NORMAL" | "S1_THROTTLE" | "S2_BARRIER" | "S3_SAFE_HALT",
        "allow_control": bool,
        "reasons": [..],
        "patch": { "mode": "...", "K": ..., "D": ..., "P_budget": ..., "G_scale": ... },
        "limits": {...}
      }

    Monotonic rule: after a violation, we only become more conservative.
    """

    cfg: SafetyConfig = field(default_factory=SafetyConfig)

    # internal latches/counters
    safe_halt_latched: bool = False
    violation_streak: int = 0
    last_state: str = "S0_NORMAL"

    # tuning: how many consecutive hard trips before SAFE_HALT
    safe_halt_after: int = 3

    def sanitize_inputs(self, sensors: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize inputs and prevent None/NaN propagation.
        Does NOT "invent" signals. Only clamps safe numeric domains.
        """
        s: Dict[str, Any] = dict(sensors or {})

        # canonical numeric fields (if present)
        for k in ("P_in", "P_draw", "Q", "phase_error", "rate_change"):
            if k in s:
                s[k] = _to_float(s.get(k))

        # clamp Q into [Q_min, Q_max] if provided
        if s.get("Q") is not None:
            s["Q"] = _clamp(float(s["Q"]), self.cfg.Q_min, self.cfg.Q_max)

        # emergency stop flag
        s["emergency_stop"] = bool(s.get("emergency_stop", False))

        # optional: tick index (for determinism)
        if "tick" in s:
            try:
                s["tick"] = int(s["tick"])
            except (TypeError, ValueError):
                s["tick"] = None

        return s

    # -------- core guard checks (strict order) --------

    def sensors_invalid(self, m: Dict[str, Any]) -> bool:
        # If emergency stop -> treat as invalid immediately
        if bool(m.get("emergency_stop", False)):
            return True

        # Missing required fields => invalid
        for k in self.cfg.require_fields:
            if m.get(k) is None:
                return True

        # Basic numeric sanity
        q = m.get("Q")
        if isinstance(q, float):
            if q < self.cfg.Q_min or q > self.cfg.Q_max:
                return True

        p_draw = m.get("P_draw")
        if isinstance(p_draw, float):
            if p_draw < 0:
                return True

        # If NaN sneaks in
        for k in ("P_in", "P_draw", "Q", "phase_error", "rate_change"):
            v = m.get(k)
            if isinstance(v, float) and (v != v):  # NaN check
                return True

        return False

    # -------- patches --------

    def _patch_none(self) -> Dict[str, Any]:
        return {"mode": "NONE"}

    def _patch_throttle(self) -> Dict[str, Any]:
        # conservative soft limitation
        return {
            "mode": "THROTTLE",
            "G_scale": 0.7,                 # reduce gain
            "K_scale": 0.7,                 # reduce coupling
            "D_boost": 1.3,                 # increase damping
            "P_budget": self.cfg.P_budget_soft,
        }

    def _patch_barrier(self) -> Dict[str, Any]:
        # Barrier = decouple + damp + cap (hard)
        return {
            "mode": "BARRIER",
            "K": 0.0,                       # decouple
            "D": "HIGH",                    # runtime maps "HIGH" to numeric
            "P_budget": self.cfg.P_budget_min,
            "freeze_fast_adaptation": True,
        }

    def _patch_safe_halt(self) -> Dict[str, Any]:
        return {
            "mode": "SAFE_HALT",
            "actuate": False,
            "K": 0.0,
            "D": "HIGH",
            "P_budget": 0.0,
        }

    # -------- evaluate --------

    def evaluate(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """
        Canonical order:
          1) Sensor validity
          2) Power overflow
          3) Coherence/Q collapse
          4) Phase runaway
          5) Rate-of-change (hard trip)
          6) Rate-of-change (soft limit)
          7) Normal envelope
          8) Default conservative
        """
        m = metrics or {}
        reasons: List[str] = []

        # Latch: SAFE_HALT stays until manual reset
        if self.safe_halt_latched:
            return self._state("S3_SAFE_HALT", allow=False, reasons=["latched_safe_halt"], patch=self._patch_safe_halt())

        # 1) Sensor validity (highest priority)
        if self.sensors_invalid(m):
            reasons.append("sensor_invalid_or_emergency_stop")
            return self._hard_violation(reasons)

        # 2) Power overflow
        p_draw = float(m["P_draw"])
        if p_draw > self.cfg.P_max:
            reasons.append(f"power_overflow:P_draw>{self.cfg.P_max}")
            return self._hard_violation(reasons)

        # 3) Coherence / Q collapse
        q = float(m["Q"])
        if q <= self.cfg.Q_crit:
            reasons.append(f"q_collapse:Q<={self.cfg.Q_crit}")
            return self._hard_violation(reasons)

        # 4) Phase runaway
        phase_err = float(m["phase_error"])
        if abs(phase_err) > self.cfg.phase_trip:
            reasons.append(f"phase_runaway:|phase_error|>{self.cfg.phase_trip}")
            return self._hard_violation(reasons)

        # 5) Rate-of-change hard trip
        rate = float(m["rate_change"])
        if abs(rate) > self.cfg.rate_trip:
            reasons.append(f"rate_trip:|rate_change|>{self.cfg.rate_trip}")
            return self._hard_violation(reasons)

        # 6) Rate-of-change soft throttle
        if abs(rate) > self.cfg.rate_limit:
            reasons.append(f"rate_limit:|rate_change|>{self.cfg.rate_limit}")
            return self._soft_violation(reasons)

        # 7) Normal envelope
        self.violation_streak = 0
        self.last_state = "S0_NORMAL"
        return self._state(
            "S0_NORMAL",
            allow=True,
            reasons=[],
            patch=self._patch_none(),
        )

    # -------- violation handlers --------

    def _hard_violation(self, reasons: List[str]) -> Dict[str, Any]:
        self.violation_streak += 1
        # escalate to SAFE_HALT if repeated
        if self.violation_streak >= self.safe_halt_after:
            self.safe_halt_latched = True
            self.last_state = "S3_SAFE_HALT"
            reasons = reasons + [f"repeated_violations>={self.safe_halt_after}"]
            return self._state("S3_SAFE_HALT", allow=False, reasons=reasons, patch=self._patch_safe_halt())

        # otherwise barrier
        self.last_state = "S2_BARRIER"
        return self._state("S2_BARRIER", allow=False, reasons=reasons, patch=self._patch_barrier())

    def _soft_violation(self, reasons: List[str]) -> Dict[str, Any]:
        # soft violations do not latch SAFE_HALT; they still count as streak
        self.violation_streak = max(self.violation_streak, 1)
        self.last_state = "S1_THROTTLE"
        return self._state("S1_THROTTLE", allow=True, reasons=reasons, patch=self._patch_throttle())

    def manual_reset(self) -> None:
        """
        Manual restart only, per spec.
        """
        self.safe_halt_latched = False
        self.violation_streak = 0
        self.last_state = "S0_NORMAL"

    def _state(self, state: str, allow: bool, reasons: List[str], patch: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "state": state,
            "allow_control": bool(allow),
            "reasons": reasons,
            "patch": patch,
            "limits": {
                "P_max": self.cfg.P_max,
                "P_budget_min": self.cfg.P_budget_min,
                "P_budget_soft": self.cfg.P_budget_soft,
                "Q_crit": self.cfg.Q_crit,
                "phase_trip": self.cfg.phase_trip,
                "rate_trip": self.cfg.rate_trip,
                "rate_limit": self.cfg.rate_limit,
            },
        }
