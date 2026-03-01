# controller/coherence_model.py
from __future__ import annotations

from dataclasses import dataclass
import numpy as np


@dataclass
class KuramotoModel:
    """
    Deterministic Kuramoto-like coherence evolution.
    No RNG. If you want initial phases, they must be provided by sensors/config.
    """
    k_gain: float = 0.25
    zeta_damp: float = 0.03

    def step(self, phases: np.ndarray, *, k_override: float | None = None) -> np.ndarray:
        if phases.size == 0:
            return phases
        k = self.k_gain if k_override is None else float(k_override)
        psi = float(np.angle(np.mean(np.exp(1j * phases))))
        d_theta = k * np.sin(psi - phases)
        phases2 = (phases + d_theta - self.zeta_damp * np.sin(phases)) % (2.0 * np.pi)
        return phases2

  
