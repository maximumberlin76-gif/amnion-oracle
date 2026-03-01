# controller/resonance_model.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional, Sequence
import math

import numpy as np


@dataclass(frozen=True)
class ResonanceFrame:
    """
    Deterministic resonance observables (no randomness).
    Produced from sensors (raw) and/or simulated signals.
    """
    state_vector: np.ndarray          # e.g., phases or embedded state
    phase_mean: float                 # mean phase (rad)
    r_order: float                    # Kuramoto order parameter (0..1)
    coherence_score: float            # normalized proxy (0..1), deterministic
    phase_noise: float                # derived noise proxy (rad or normalized)
    q_factor: float                   # derived stability proxy (0..1)


def _safe_array(x: Any) -> np.ndarray:
    if x is None:
        return np.zeros((0,), dtype=float)
    arr = np.asarray(x, dtype=float).reshape(-1)
    return arr


def _kuramoto_r_order(phases: np.ndarray) -> float:
    if phases.size == 0:
        return 0.0
    z = np.mean(np.exp(1j * phases))
    return float(np.clip(np.abs(z), 0.0, 1.0))


def _phase_mean(phases: np.ndarray) -> float:
    if phases.size == 0:
        return 0.0
    z = np.mean(np.exp(1j * phases))
    return float(np.angle(z))


def from_sensors(sensors: Dict[str, Any], *, phases_key: str = "phase_samples") -> ResonanceFrame:
    """
    Expected input patterns (choose one, keep deterministic):
      - sensors[phases_key] = array-like of phases (rad)
      - OR sensors["signal"] = array-like raw waveform (will be embedded deterministically)
    """
    sensors = sensors or {}

    phases = _safe_array(sensors.get(phases_key))
    if phases.size == 0:
        # deterministic fallback: if we have a waveform, build a phase-like embedding
        sig = _safe_array(sensors.get("signal"))
        if sig.size > 0:
            sig0 = sig - float(np.mean(sig))
            # deterministic sign-phase embedding (cheap)
            phases = np.where(sig0 >= 0.0, 0.0, math.pi).astype(float)

    r = _kuramoto_r_order(phases)
    mu = _phase_mean(phases)

    # deterministic noise proxy: dispersion around mean phase
    if phases.size == 0:
        phase_noise = 1.0
    else:
        # circular distance
        d = np.angle(np.exp(1j * (phases - mu)))
        phase_noise = float(np.clip(np.std(d), 0.0, math.pi))

    # coherence_score: map r_order and noise into 0..1 deterministically
    coherence_score = float(np.clip(0.7 * r + 0.3 * (1.0 - phase_noise / math.pi), 0.0, 1.0))

    # q_factor proxy: keep it explicit (docs map this)
    q_factor = float(coherence_score)

    return ResonanceFrame(
        state_vector=phases,
        phase_mean=mu,
        r_order=r,
        coherence_score=coherence_score,
        phase_noise=phase_noise,
        q_factor=q_factor,
    )
  
