# controller/safety_gate.py
# Safety gate for AMNION-ORACLE (documentation-first).
# Produces monotonic safety decisions: NORMAL -> THROTTLE -> BARRIER -> SAFE_HALT.
# No clinical use.

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


def clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))


@dataclass
class SafetyConfig:
    # Canonical power limits (concept-level)
    P_max: float = 1.0
    P_budget_min: float = 0.0
    P_budget_soft: float = 0.8

    # Coherence / Q thresholds
    Q_crit: float = 0.50

    # Phase thresholds
    phase_trip: float = 0.50  # rad (or proxy units)

    # Rate thresholds (two-tier)
    rate_trip: float = 1.00
    rate_limit: float = 0.50

    # Optional ABRAXAS invariants (concept-level, may be absent)
    f_ref_nominal: float = 76.4
    f_tol: float = 0.5
    integrity_min: float = 0.90

    # Monotonic behavior: once escalated, do not de-escalate automatically within same tick
    monotonic: bool = True


@dataclass
class SafetyGate:
    cfg: SafetyConfig = field(default_factory=SafetyConfig)

    def sanitize_inputs(self, sensors: Dict[str, Any]) -> Dict[str, Any]:
        """
        Defensive normalization:
        - Always returns a dict
        - No exceptions
        - Keeps original keys but adds normalized aliases when possible
        """
        sensors = sensors or {}
        out: Dict[str, Any] = dict(sensors)

        # Normalize common names (support both spec-style and casual keys)
        # Power
        if "P_in" not in out and "power_in" in out:
            out["P_in"] = out.get("power_in")
        if "P_draw" not in out and "power_draw" in out:
            out["P_draw"] = out.get("power_draw")

        # Phase
        if "phase_error" not in out and "mismatch_phase" in out:
            out["phase_error"] = out.get("mismatch_phase")

        # Q / coherence
        if "Q" not in out and "q" in out:
            out["Q"] = out.get("q")

        # Optional: coherence proxy
        if "coherence" not in out and "C" in out:
            out["coherence"] = out.get("C")

        return out

    def evaluate(self, sensors: Dict[str, Any]) -> Dict[str, Any]:
        """
        Returns a safety_state dict consumed by Runtime:
          {
            "ok": bool,
            "allow_control": bool,
            "state": "S0_NORMAL"|"S1_THROTTLE"|"S2_BARRIER"|"S3_SAFE_HALT",
            "flags": [...],
            "limits": {...},
            "patch": {...},
            "mismatch_power": float|None,
            "mismatch_phase": float|None,
          }
        """
        sensors = sensors or {}
        flags: List[str] = []

        # --- Extract metrics (best-effort) ---
        P_in = _to_float(sensors.get("P_in"))
        P_draw = _to_float(sensors.get("P_draw"))
        Q = _to_float(sensors.get("Q"))
        phase_error = _to_float(sensors.get("phase_error"))
        rate_change = _to_float(sensors.get("rate_change"))

        emergency_stop = bool(sensors.get("emergency_stop", False))

        # Optional ABRAXAS keys
        f_ref = _to_float(sensors.get("f_ref"))
        loop_closure = sensors.get("loop_closure")
        state_integrity = _to_float(sensors.get("state_integrity"))

        # --- Sensor validity check (highest priority) ---
        sensors_invalid = False
        # Treat any explicit invalid flag as invalid
        if sensors.get("sensor_valid") is False:
            sensors_invalid = True
            flags.append("sensor_invalid:flag")

        # Missing critical metrics counts as invalid for guard purposes
        # (We keep it conservative but deterministic)
        if Q is None:
            sensors_invalid = True
            flags.append("sensor_invalid:missing_Q")

        # Power signals are optional for running, but if one present and the other missing we mark uncertainty
        if (P_in is None) != (P_draw is None):
            flags.append("sensor_uncertain:power_partial")

        if emergency_stop:
            flags.append("emergency_stop=true")

        # --- Compute mismatches (if possible) ---
        mismatch_power: Optional[float] = None
        if P_in is not None and P_draw is not None:
            mismatch_power = P_draw - P_in

        mismatch_phase: Optional[float] = None
        if phase_error is not None:
            mismatch_phase = abs(phase_error)

        # --- Escalation decision (canonical order) ---
        state = "S0_NORMAL"
        allow_control = True

        # Helper to escalate monotonically
        def _escalate(new_state: str) -> None:
            nonlocal state
            order = {"S0_NORMAL": 0, "S1_THROTTLE": 1, "S2_BARRIER": 2, "S3_SAFE_HALT": 3}
            if order.get(new_state, 0) > order.get(state, 0):
                state = new_state

        # 0) Emergency stop -> SAFE_HALT
        if emergency_stop:
            _escalate("S3_SAFE_HALT")

        # 1) Sensor invalid / missing -> BARRIER (or SAFE_HALT if combined with emergency)
        if sensors_invalid:
            _escalate("S2_BARRIER")

        # 2) Power overflow -> BARRIER (only if we can measure)
        if P_draw is not None and P_draw > self.cfg.P_max:
            flags.append("power_overflow")
            _escalate("S2_BARRIER")

        # 3) Coherence / Q collapse -> BARRIER
        if Q is not None and Q <= self.cfg.Q_crit:
            flags.append("Q_crit")
            _escalate("S2_BARRIER")

        # 4) Phase runaway -> BARRIER (if measurable)
        if mismatch_phase is not None and mismatch_phase > self.cfg.phase_trip:
            flags.append("phase_trip")
            _escalate("S2_BARRIER")

        # 5) Rate-of-change -> two-tier
        if rate_change is not None and abs(rate_change) > self.cfg.rate_trip:
            flags.append("rate_trip")
            _escalate("S2_BARRIER")
        elif rate_change is not None and abs(rate_change) > self.cfg.rate_limit:
            flags.append("rate_limit")
            _escalate("S1_THROTTLE")

        # 6) ABRAXAS invariants (optional, only if provided)
        if f_ref is not None:
            if abs(f_ref - self.cfg.f_ref_nominal) > self.cfg.f_tol:
                flags.append("abraxas:f_ref_outside_tol")
                _escalate("S2_BARRIER")

        if loop_closure is not None:
            # Accept True/False or 1/0 or "true"/"false"
            lc = loop_closure
            if isinstance(lc, str):
                lc = lc.strip().lower() in ("1", "true", "yes", "y")
            lc_bool = bool(lc)
            if not lc_bool:
                flags.append("abraxas:loop_not_closed")
                _escalate("S2_BARRIER")

        if state_integrity is not None:
            if state_integrity < self.cfg.integrity_min:
                flags.append("abraxas:state_integrity_low")
                _escalate("S2_BARRIER")

        # Determine allow_control
        if state in ("S2_BARRIER", "S3_SAFE_HALT"):
            allow_control = False

        # --- Patch construction (what Runtime will apply) ---
        patch: Dict[str, Any] = {"mode": "NONE"}

        if state == "S3_SAFE_HALT":
            patch = {
                "mode": "SAFE_HALT",
                "D": "HIGH",
                "P_budget": 0.0,
                "freeze_fast_adaptation": True,
            }
        elif state == "S2_BARRIER":
            patch = {
                "mode": "BARRIER",
                "D": "HIGH",
                "P_budget": self.cfg.P_budget_min,
                "freeze_fast_adaptation": True,
            }
        elif state == "S1_THROTTLE":
            patch = {
                "mode": "THROTTLE",
                "G_scale": 0.5,
                "K_scale": 0.5,
                "D_boost": 2.0,
                "P_budget": self.cfg.P_budget_soft,
            }

        limits = {
            "P_max": self.cfg.P_max,
            "P_budget_min": self.cfg.P_budget_min,
            "P_budget_soft": self.cfg.P_budget_soft,
            "Q_crit": self.cfg.Q_crit,
            "phase_trip": self.cfg.phase_trip,
            "rate_trip": self.cfg.rate_trip,
            "rate_limit": self.cfg.rate_limit,
        }

        ok = allow_control and state == "S0_NORMAL"

        return {
            "ok": ok,
            "allow_control": allow_control,
            "state": state,
            "flags": flags,
            "limits": limits,
            "patch": patch,
            "mismatch_power": mismatch_power,
            "mismatch_phase": mismatch_phase,
        }
