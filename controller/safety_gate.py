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


def _to_bool(x: Any) -> Optional[bool]:
    if x is None:
        return None
    if isinstance(x, bool):
        return x
    if isinstance(x, (int, float)):
        return bool(x)
    if isinstance(x, str):
        return x.strip().lower() in ("1", "true", "yes", "y", "on")
    return bool(x)


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

    # LawX mapping (concept-level)
    lawx_throttle_to: str = "S1_THROTTLE"   # THROTTLE -> THROTTLE
    lawx_isolate_to: str = "S2_BARRIER"    # ISOLATE -> BARRIER
    lawx_degrade_to: str = "S3_SAFE_HALT"  # DEGRADE -> SAFE_HALT (жёстко и правильно)

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

        # Power aliases
        if "P_in" not in out and "power_in" in out:
            out["P_in"] = out.get("power_in")
        if "P_draw" not in out and "power_draw" in out:
            out["P_draw"] = out.get("power_draw")
        if "P_draw" not in out and "power_w" in out:
            out["P_draw"] = out.get("power_w")

        # Phase aliases
        if "phase_error" not in out and "mismatch_phase" in out:
            out["phase_error"] = out.get("mismatch_phase")
        if "phase_error" not in out and "phase_noise" in out:
            out["phase_error"] = out.get("phase_noise")

        # Q / coherence aliases (priority: explicit Q > q_factor > coherence_score)
        if "Q" not in out and "q" in out:
            out["Q"] = out.get("q")
        if "Q" not in out and "q_factor" in out:
            out["Q"] = out.get("q_factor")
        if "Q" not in out and "coherence_score" in out:
            out["Q"] = out.get("coherence_score")

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

        # LawX (optional)
        lawx_mode = sensors.get("lawx_mode", sensors.get("lawx_rec", None))
        if isinstance(lawx_mode, str):
            lawx_mode = lawx_mode.strip().upper()
        else:
            lawx_mode = None

        lawx_conf = _to_float(sensors.get("lawx_confidence"))
        lawx_pattern = sensors.get("lawx_pattern")

        # ABRAXAS (optional, can come as precomputed violations)
        abraxas_violation_count = sensors.get("abraxas_violation_count")
        abraxas_violations = sensors.get("abraxas_violations")

        # Legacy/explicit ABRAXAS keys (still supported)
        f_ref = _to_float(sensors.get("f_ref"))
        loop_closure = _to_bool(sensors.get("loop_closure"))
        state_integrity = _to_float(sensors.get("state_integrity"))

        # --- Sensor validity check (highest priority) ---
        sensors_invalid = False

        if sensors.get("sensor_valid") is False:
            sensors_invalid = True
            flags.append("sensor_invalid:flag")

        # Missing Q is invalid (deterministic conservative stance)
        if Q is None:
            sensors_invalid = True
            flags.append("sensor_invalid:missing_Q")

        # Power partial is uncertainty (not invalid)
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

        def _escalate(new_state: str) -> None:
            nonlocal state
            order = {"S0_NORMAL": 0, "S1_THROTTLE": 1, "S2_BARRIER": 2, "S3_SAFE_HALT": 3}
            if order.get(new_state, 0) > order.get(state, 0):
                state = new_state

        # 0) Emergency stop -> SAFE_HALT
        if emergency_stop:
            _escalate("S3_SAFE_HALT")

        # 1) Sensor invalid -> BARRIER
        if sensors_invalid:
            _escalate("S2_BARRIER")

        # 2) LawX escalation (if present)
        # NOTE: We treat LawX as an upstream detector; mapping is explicit and deterministic.
        if lawx_mode in ("DEGRADE",):
            flags.append("lawx:DEGRADE")
            if lawx_pattern:
                flags.append(f"lawx_pattern:{lawx_pattern}")
            _escalate(self.cfg.lawx_degrade_to)
        elif lawx_mode in ("ISOLATE",):
            flags.append("lawx:ISOLATE")
            if lawx_pattern:
                flags.append(f"lawx_pattern:{lawx_pattern}")
            _escalate(self.cfg.lawx_isolate_to)
        elif lawx_mode in ("THROTTLE",):
            flags.append("lawx:THROTTLE")
            if lawx_conf is not None and lawx_conf >= 0.8:
                flags.append("lawx_conf:high")
            _escalate(self.cfg.lawx_throttle_to)
        elif lawx_mode in ("ALLOW", None):
            pass
        else:
            # Unknown mode -> conservative throttle (not barrier)
            flags.append("lawx:UNKNOWN_MODE")
            _escalate("S1_THROTTLE")

        # 3) Power overflow -> BARRIER (only if measurable)
        if P_draw is not None and P_draw > self.cfg.P_max:
            flags.append("power_overflow")
            _escalate("S2_BARRIER")

        # 4) Coherence / Q collapse -> BARRIER
        if Q is not None and Q <= self.cfg.Q_crit:
            flags.append("Q_crit")
            _escalate("S2_BARRIER")

        # 5) Phase runaway -> BARRIER (if measurable)
        if mismatch_phase is not None and mismatch_phase > self.cfg.phase_trip:
            flags.append("phase_trip")
            _escalate("S2_BARRIER")

        # 6) Rate-of-change -> two-tier
        if rate_change is not None and abs(rate_change) > self.cfg.rate_trip:
            flags.append("rate_trip")
            _escalate("S2_BARRIER")
        elif rate_change is not None and abs(rate_change) > self.cfg.rate_limit:
            flags.append("rate_limit")
            _escalate("S1_THROTTLE")

        # 7) ABRAXAS invariants (preferred: precomputed violations from controller)
        if abraxas_violation_count is not None:
            try:
                cnt = int(abraxas_violation_count)
            except Exception:
                cnt = 0
            if cnt > 0:
                flags.append("abraxas:violation_count>0")
                if isinstance(abraxas_violations, list):
                    for v in abraxas_violations[:6]:
                        flags.append(f"abraxas:{v}")
                _escalate("S2_BARRIER")

        else:
            # Legacy evaluation if no precomputed violations exist
            if f_ref is not None:
                if abs(f_ref - self.cfg.f_ref_nominal) > self.cfg.f_tol:
                    flags.append("abraxas:f_ref_outside_tol")
                    _escalate("S2_BARRIER")

            if loop_closure is not None:
                if not bool(loop_closure):
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
            "f_ref_nominal": self.cfg.f_ref_nominal,
            "f_tol": self.cfg.f_tol,
            "integrity_min": self.cfg.integrity_min,
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
        
