# controller/amnion_controller.py
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict

from controller.metrics import Metrics
from controller.runtime import Runtime
from controller.safety_gate import SafetyGate

from controller.resonance_model import from_sensors as resonance_from_sensors
from controller.lawx_adapter import LawXAdapter
from controller.abraxas_module import AbraxasModule


@dataclass
class AmnionController:
    """
    Deterministic orchestration layer.

    Responsibilities:
        - sanitize inputs
        - derive resonance observables
        - run LawX (optional)
        - run ABRAXAS invariants (optional)
        - evaluate safety state machine
        - compute runtime output with hard clamps
        - update metrics/logging

    No randomness, no hidden sampling, no medical claims.
    """

    safety: SafetyGate = field(default_factory=SafetyGate)
    metrics: Metrics = field(default_factory=lambda: Metrics(cfg={}))
    runtime: Runtime = field(default_factory=Runtime)

    # optional modules
    lawx: LawXAdapter = field(default_factory=LawXAdapter)
    abraxas: AbraxasModule = field(default_factory=AbraxasModule)

    def step(self, sensors: Dict[str, Any]) -> Dict[str, Any]:
        sensors = sensors or {}

        # ------------------------------------------------------------
        # 1) Sanitize inputs (must never throw)
        # ------------------------------------------------------------
        safe_sensors = self.safety.sanitize_inputs(sensors)

        # ------------------------------------------------------------
        # 2) Resonance layer (physical observables, deterministic)
        # ------------------------------------------------------------
        try:
            rf = resonance_from_sensors(safe_sensors)
        except Exception:
            rf = None

        if rf is not None:
            safe_sensors = dict(safe_sensors)
            safe_sensors.update({
                "r_order": rf.r_order,
                "phase_mean": rf.phase_mean,
                "phase_noise": rf.phase_noise,
                "q_factor": rf.q_factor,
                "coherence_score": rf.coherence_score,
                # if resonance_model exposes it; safe to ignore if absent
                "state_vector": getattr(rf, "state_vector", None),
            })

        # ------------------------------------------------------------
        # 3) LawX (optional, must never throw)
        # ------------------------------------------------------------
        lawx_res = self.lawx.process(safe_sensors)
        if lawx_res is not None:
            safe_sensors = dict(safe_sensors)
            safe_sensors.update({
                "lawx_mode": lawx_res.mode,
                "lawx_confidence": lawx_res.confidence,
                "lawx_pattern": lawx_res.pattern,
                "attack_signature": lawx_res.attack_signature,
                "lawx_state_l0": lawx_res.state_l0,
                "lawx_q_est": lawx_res.q_est,
                "lawx_r_order": lawx_res.r_order,
                "lawx_phase_mismatch": lawx_res.phase_mismatch,
                "lawx_power_noise": lawx_res.power_noise,
                "lawx_gap": lawx_res.gap,
                "lawx_p_draw": lawx_res.p_draw,
            })

        # ------------------------------------------------------------
        # 4) ABRAXAS invariants (optional, deterministic)
        # ------------------------------------------------------------
        abra = self.abraxas.evaluate(safe_sensors)
        safe_sensors = dict(safe_sensors)
        safe_sensors.update({
            "f_ref": abra.f_ref,
            "f_tol": abra.f_tol,
            "phase_error": abra.phase_error,
            "loop_closure": abra.loop_closure,
            "state_integrity": abra.state_integrity,
            "integrity_min": abra.integrity_min,
            "abraxas_violations": list(abra.violations),
            "abraxas_violation_count": len(abra.violations),
        })

        # ------------------------------------------------------------
        # 5) Safety evaluation (state machine / barrier logic)
        # ------------------------------------------------------------
        safety_state = self.safety.evaluate(safe_sensors)

        # ------------------------------------------------------------
        # 6) Runtime decision (hard clamps applied here)
        # ------------------------------------------------------------
        output = self.runtime.compute(safe_sensors, safety_state)

        # ------------------------------------------------------------
        # 7) Metrics logging (best-effort only)
        # ------------------------------------------------------------
        try:
            self.metrics.on_tick(safe_sensors, safety_state, output)
        except Exception:
            pass

        return output
