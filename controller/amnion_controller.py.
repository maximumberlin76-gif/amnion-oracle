# controller/amnion_controller.py
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict

from controller.metrics import Metrics
from controller.runtime import Runtime
from controller.safety_gate import SafetyGate


@dataclass
class AmnionController:
    safety: SafetyGate = field(default_factory=SafetyGate)
    metrics: Metrics = field(default_factory=lambda: Metrics(cfg={}))
    runtime: Runtime = field(default_factory=Runtime)

    def step(self, sensors: Dict[str, Any]) -> Dict[str, Any]:
        """
        One control tick:
        sensors -> safety -> runtime decision -> metrics update -> output
        """
        sensors = sensors or {}

        # Safety gate must never throw
        safe_sensors = self.safety.sanitize_inputs(sensors)

        # Evaluate safety state (state + patch + limits)
        safety_state = self.safety.evaluate(safe_sensors)

        # Runtime computes final control_frame with hard clamps
        output = self.runtime.compute(safe_sensors, safety_state)

        # Metrics (best-effort, must not break loop)
        try:
            self.metrics.on_tick(safe_sensors, safety_state, output)
        except Exception:
            pass

        return output

    def compute_coherence(self, sensors: Dict[str, Any]) -> float:
        """
        Coherence proxy: ratio of non-negative numeric fields among numeric fields.
        """
        if not sensors:
            return 0.0

        valid = 0
        total = 0

        for v in sensors.values():
            if isinstance(v, (int, float)):
                total += 1
                if v >= 0:
                    valid += 1

        if total == 0:
            return 0.0

        return valid / total
