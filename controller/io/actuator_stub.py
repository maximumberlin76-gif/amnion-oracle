# controller/io/actuator_stub.py
# Simulation-only actuator layer.
# No physical actuation.

from __future__ import annotations

from typing import Dict, Any


class ActuatorStub:
    """
    Actuator stub for simulation mode.

    This module DOES NOT control real hardware.
    It only records intended outputs.
    """

    def __init__(self):
        self.last_output: Dict[str, Any] = {}

    def apply(self, control_frame: Dict[str, Any]) -> None:
        """
        Store control output for inspection.
        No external effect.
        """
        self.last_output = dict(control_frame)

    def get_last(self) -> Dict[str, Any]:
        return dict(self.last_output)

  
