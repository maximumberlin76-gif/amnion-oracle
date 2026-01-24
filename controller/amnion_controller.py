from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

from .config_loader import load_config_bundle
from .logger import get_logger
from .safety_gate import SafetyGate
from .metrics import Metrics
from .runtime import Runtime


@dataclass
class AmnionController:
    """
    Main orchestrator:
    - loads configs bundle
    - initializes logger, safety gate, metrics, runtime
    - provides a single 'step' entrypoint for the control loop
    """
    cfg_dir: str = "configs"
    config_files: Optional[list[str]] = None  # allow override
    log = None

    def __post_init__(self) -> None:
        self.log = get_logger("amnion")

        # canonical order (your numbering): 00..06 + manifest
        default_files = [
            "00_system.yaml",
            "01_interfaces.yaml",
            "02_safety.yaml",
            "03_metrics.yaml",
            "04_logging.yaml",
            "05_profile.yaml",
            "06_safeguards.yaml",
        ]
        files = self.config_files or default_files

        self.cfg: Dict[str, Any] = load_config_bundle(self.cfg_dir, files)

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

