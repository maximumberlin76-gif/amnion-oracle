# controller/amnion_controller.py
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict

from controller.metrics import Metrics
from controller.runtime import Runtime
from controller.safety_gate import SafetyGate
from controller.resonance_model import from_sensors as resonance_from_sensors


@dataclass
class AmnionController:
    """
    Deterministic orchestration layer.

    Responsibilities:
        - sanitize inputs
        - derive resonance observables
        - evaluate safety state
        - compute runtime output
        - update metrics

    No physics, no randomness, no policy overrides.
    """

    safety: SafetyGate = field(default_factory=SafetyGate)
    metrics: Metrics = field(default_factory=lambda: Metrics(cfg={}))
    runtime: Runtime = field(default_factory=Runtime)

    def step(self, sensors: Dict[str, Any]) -> Dict[str, Any]:
        """
        One deterministic control tick:

            raw sensors
                → sanitize
                → resonance derivation
                → safety evaluation
                → runtime compute
                → metrics update
                → output
        """

        sensors = sensors or {}

        # ------------------------------------------------------------------
        # 1) Sanitize inputs (must never throw)
        # ------------------------------------------------------------------
        safe_sensors = self.safety.sanitize_inputs(sensors)

        # ------------------------------------------------------------------
        # 2) Resonance layer (deterministic physics observables)
        # ------------------------------------------------------------------
        try:
            rf = resonance_from_sensors(safe_sensors)
        except Exception:
            # Resonance layer must never break control loop
            rf = None

        if rf is not None:
            # Attach derived metrics for downstream modules
            safe_sensors = dict(safe_sensors)
            safe_sensors.update({
                "r_order": rf.r_order,
                "phase_mean": rf.phase_mean,
                "phase_noise": rf.phase_noise,
                "q_factor": rf.q_factor,
                "coherence_score": rf.coherence_score,
            })

        # ------------------------------------------------------------------
        # 3) Safety evaluation (state machine / barrier logic)
        # ------------------------------------------------------------------
        safety_state = self.safety.evaluate(safe_sensors)

        # ------------------------------------------------------------------
        # 4) Runtime decision (hard clamps applied here)
        # ------------------------------------------------------------------
        output = self.runtime.compute(safe_sensors, safety_state)

        # ------------------------------------------------------------------
        # 5) Metrics logging (best-effort only)
        # ------------------------------------------------------------------
        try:
            self.metrics.on_tick(safe_sensors, safety_state, output)
        except Exception:
            pass

        return output

