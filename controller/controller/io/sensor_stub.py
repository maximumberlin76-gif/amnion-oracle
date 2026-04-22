# controller/io/sensor_stub.py
# Simulation-only sensor layer for AMNION-ORACLE
# No hardware I/O. Deterministic synthetic frames.

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Any
import math


@dataclass
class SensorStubConfig:
    base_freq: float = 76.4
    q_start: float = 0.92
    q_decay_per_tick: float = 0.00005
    p_in_nominal: float = 0.50
    p_draw_base: float = 0.45
    p_draw_amp: float = 0.08
    phase_amp: float = 0.20
    rate_amp: float = 0.01


class SensorStub:
    """
    Deterministic synthetic sensor source.

    Produces stable, non-random frames for controller testing.
    No hardware access.
    """

    def __init__(self, cfg: SensorStubConfig | None = None):
        self.cfg = cfg or SensorStubConfig()
        self.tick_index = 0

    def read(self) -> Dict[str, Any]:
        t = float(self.tick_index)
        self.tick_index += 1

        phase = 0.05 * t
        q_val = max(0.0, self.cfg.q_start - self.cfg.q_decay_per_tick * t)

        p_in = self.cfg.p_in_nominal
        p_draw = self.cfg.p_draw_base + self.cfg.p_draw_amp * math.sin(phase)
        phase_error = abs(math.sin(phase)) * self.cfg.phase_amp
        rate_change = self.cfg.rate_amp * math.cos(phase)

        return {
            "ts": t,
            "f_ref": self.cfg.base_freq,
            "P_in": p_in,
            "P_draw": p_draw,
            "Q": q_val,
            "phase_error": phase_error,
            "rate_change": rate_change,
            "temp_c": 24.0 + 0.2 * math.sin(phase / 2.0),
            "loop_closure": True,
            "state_integrity": 0.95,
            "sensor_valid": True,
            "emergency_stop": False,
        }
