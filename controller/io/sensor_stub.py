# controller/io/sensor_stub.py
# Simulation-only sensor layer.
# No physical I/O. No hardware bindings.

from __future__ import annotations

import math
import time
from typing import Dict, Any


class SensorStub:
    """
    Deterministic sensor simulation.

    This module produces synthetic sensor frames
    for reproducible controller ticks.

    No hardware access is implemented.
    """

    def __init__(self, base_freq: float = 76.4):
        self.base_freq = float(base_freq)
        self._t0 = time.time()
        self._tick = 0

    def read(self) -> Dict[str, Any]:
        """
        Produce a synthetic sensor frame.
        Fully deterministic given tick index.
        """
        t = self._tick
        self._tick += 1

        # Simple deterministic waveforms
        phase = 0.05 * t
        q = 0.9 - 0.0001 * t  # slight decay
        power_draw = 0.5 + 0.1 * math.sin(phase)
        power_in = 0.5

        return {
            "ts": time.time(),
            "f_ref": self.base_freq,
            "phase_error": abs(math.sin(phase)) * 0.2,
            "Q": max(0.0, q),
            "P_draw": power_draw,
            "P_in": power_in,
            "rate_change": 0.01 * math.cos(phase),
            "loop_closure": True,
            "state_integrity": 0.95,
            "sensor_valid": True,
            "emergency_stop": False,
        }

  
