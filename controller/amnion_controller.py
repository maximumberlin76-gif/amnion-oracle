# controller/amnion_controller.py
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any, Dict, Optional

from controller.metrics import Metrics
from controller.runtime import Runtime
from controller.safety_gate import SafetyGate
from controller.resonance_model import from_sensors as resonance_from_sensors
from controller.lawx_adapter import LawXAdapter
from controller.abraxas_module import AbraxasModule
from controller.contracts import SensorFrame, DerivedMetrics, SafetyState, ControlOutput


@dataclass
class AmnionController:
    """
    Deterministic orchestration layer for AMNION-ORACLE.

    Flow:
        raw sensors
          -> sanitize
          -> resonance derivation
          -> LawX advisory
          -> ABRAXAS invariants
          -> safety evaluation
          -> runtime compute
          -> metrics logging
    """

    safety: SafetyGate = field(default_factory=SafetyGate)
    metrics: Metrics = field(default_factory=lambda: Metrics(cfg={}))
    runtime: Runtime = field(default_factory=Runtime)
    lawx: LawXAdapter = field(default_factory=LawXAdapter)
    abraxas: AbraxasModule = field(default_factory=AbraxasModule)

    @staticmethod
    def _to_float(x: Any) -> Optional[float]:
        try:
            return None if x is None else float(x)
        except Exception:
            return None

    def _to_sensor_frame(self, sensors: Dict[str, Any]) -> SensorFrame:
        return SensorFrame(
            P_in=self._to_float(sensors.get("P_in")),
            P_draw=self._to_float(sensors.get("P_draw")),
            Q=self._to_float(sensors.get("Q")),
            phase_error=self._to_float(sensors.get("phase_error")),
            temp_c=self._to_float(sensors.get("temp_c")),
            sensor_valid=bool(sensors.get("sensor_valid", True)),
        )

    def _derive_metrics(self, sensor_frame: SensorFrame, enriched: Dict[str, Any]) -> DerivedMetrics:
        mismatch_power: Optional[float] = None
        if sensor_frame.P_in is not None and sensor_frame.P_draw is not None:
            mismatch_power = sensor_frame.P_draw - sensor_frame.P_in

        mismatch_phase: Optional[float] = None
        if sensor_frame.phase_error is not None:
            mismatch_phase = abs(sensor_frame.phase_error)

        coherence_score = self._to_float(enriched.get("coherence_score")) or 0.0

        return DerivedMetrics(
            mismatch_power=mismatch_power,
            mismatch_phase=mismatch_phase,
            coherence_score=coherence_score,
        )

    def step(self, sensors: Dict[str, Any]) -> Dict[str, Any]:
        sensors = sensors or {}

        # ------------------------------------------------------------
        # 1) Sanitize inputs
        # ------------------------------------------------------------
        safe_sensors = self.safety.sanitize_inputs(sensors)

        # ------------------------------------------------------------
        # 2) Resonance layer (deterministic physical observables)
        # ------------------------------------------------------------
        try:
            rf = resonance_from_sensors(safe_sensors)
            safe_sensors = dict(safe_sensors)
            safe_sensors.update({
                "r_order": rf.r_order,
                "phase_mean": rf.phase_mean,
                "phase_noise": rf.phase_noise,
                "q_factor": rf.q_factor,
                "coherence_score": rf.coherence_score,
                "state_vector": getattr(rf, "state_vector", None),
            })
        except Exception:
            # resonance layer must never break the control loop
            pass

        # ------------------------------------------------------------
        # 3) LawX advisory
        # ------------------------------------------------------------
        try:
            lawx_res = self.lawx.process(safe_sensors)
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
        except Exception:
            pass

        # ------------------------------------------------------------
        # 4) ABRAXAS invariants
        # ------------------------------------------------------------
        try:
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
        except Exception:
            pass

        # ------------------------------------------------------------
        # 5) Typed views
        # ------------------------------------------------------------
        sensor_frame = self._to_sensor_frame(safe_sensors)
        derived = self._derive_metrics(sensor_frame, safe_sensors)

        # ------------------------------------------------------------
        # 6) Safety evaluation
        # ------------------------------------------------------------
        raw_safety = self.safety.evaluate(safe_sensors)
        safety_state = SafetyState(
            state=str(raw_safety.get("state", "S0_NORMAL")),
            allow_control=bool(raw_safety.get("allow_control", True)),
            P_budget=float(raw_safety.get("patch", {}).get("P_budget", 0.0) or 0.0),
        )

        # ------------------------------------------------------------
        # 7) Runtime compute
        # ------------------------------------------------------------
        raw_output = self.runtime.compute(safe_sensors, raw_safety)
        control_output = ControlOutput(
            u_control=float(raw_output.get("u_control", 0.0) or 0.0),
            mode=str(raw_output.get("mode", raw_safety.get("patch", {}).get("mode", "NORMAL"))),
            P_budget=float(raw_output.get("P_budget", safety_state.P_budget) or 0.0),
        )

        # ------------------------------------------------------------
        # 8) Metrics logging (best-effort)
        # ------------------------------------------------------------
        try:
            self.metrics.on_tick(
                {
                    **safe_sensors,
                    "sensor_frame": asdict(sensor_frame),
                    "derived_metrics": asdict(derived),
                },
                raw_safety,
                asdict(control_output),
            )
        except Exception:
            pass

        # ------------------------------------------------------------
        # 9) Public return payload
        # ------------------------------------------------------------
        return {
            **asdict(control_output),
            "state": safety_state.state,
            "allow_control": safety_state.allow_control,
            "derived_metrics": asdict(derived),
        }
