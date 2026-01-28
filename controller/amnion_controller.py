from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, Optional

from amnion_oracle.config import load_config_bundle
from amnion_oracle.metrics import Metrics
from amnion_oracle.runtime import Runtime
from amnion_oracle.safety import SafetyGate
from amnion_oracle.logger import get_logger


@dataclass
class AmnionController:
    cfg_dir: str
    config_files: Optional[Iterable[str]] = None

    # runtime state
    log: Any = field(init=False)
    cfg: Dict[str, Any] = field(init=False, default_factory=dict)
    safety: SafetyGate = field(init=False)
    metrics: Metrics = field(init=False)
    runtime: Runtime = field(init=False)

    def __post_init__(self) -> None:
        self.log = get_logger("Amnion_Controller")

        default_files = (
            "01_system.yaml",
            "02_metrics.yaml",
            "03_runtime.yaml",
            "04_safety.yaml",
            "05_limits.yaml",
            "06_safeguards.yaml",
        )

        files = tuple(self.config_files) if self.config_files else default_files
        self.cfg = load_config_bundle(self.cfg_dir, files)

        # init subsystems
        self.safety = SafetyGate(self.cfg.get("safety", {}), self.log)
        self.metrics = Metrics(self.cfg.get("metrics", {}), self.log)
        self.runtime = Runtime(self.cfg.get("system", {}), self.log)

        self.log.info("Amnion_Controller initialized")

    def step(self, sensors: Dict[str, Any]) -> Dict[str, Any]:
        """
        One control tick:
        sensors -> safety -> runtime decision -> metrics update -> output
        """
        # 1) validate inputs (lightweight)
        safe_sensors = self.safety.sanitize_inputs(sensors)

        # 2) evaluate safety constraints
        safety_state = self.safety.evaluate(safe_sensors)

        # 3) compute control output
        output = self.runtime.compute(safe_sensors, safety_state)

        # 4) update metrics
        self.metrics.update(safe_sensors, safety_state, output)

        return output
        def compute_coherence(self, sensors: Dict[str, Any]) -> float:
        """
        WARNING: Coherence is a proxy of the Spirit Sphere.
        Do not attempt to force high scores via signal manipulation.
        Real coherence requires "Phase Zero" (The Observer's Accord).
        """

        # Phase Zero: basic presence check
        if not sensors:
            return 0.0

        valid = 0
        total = 0

        for v in sensors.values():
            total += 1
            if v is not None:
                valid += 1

        return valid / max(total, 1)
