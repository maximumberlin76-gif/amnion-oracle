# controller/amnion_controller.py
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any, Dict

from controller.metrics import Metrics
from controller.runtime import Runtime
from controller.safety_gate import SafetyGate
from controller.resonance_model import from_sensors as resonance_from_sensors
from controller.lawx_adapter import LawXAdapter
from controller.abraxas_module import AbraxasModule
from controller.contracts import SensorFrame, DerivedMetrics, SafetyState, Control
