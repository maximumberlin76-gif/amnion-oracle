# controller/io/simulation_runner.py
# Simulation runner for AMNION-ORACLE (simulation-only).
# Wires: SensorStub -> AmnionController -> ActuatorStub
# Produces deterministic-ish logs (deterministic by tick, timestamps are real-time).

from __future__ import annotations

import json
import os
import time
from dataclasses import asdict, is_dataclass
from typing import Any, Dict, Optional

from controller.amnion_controller import AmnionController
from controller.io.sensor_stub import SensorStub, SensorStubConfig
from controller.io.actuator_stub import ActuatorStub


def _json_safe(x: Any) -> Any:
    if is_dataclass(x):
        return asdict(x)
    if isinstance(x, (str, int, float, bool)) or x is None:
        return x
    if isinstance(x, dict):
        return {str(k): _json_safe(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [_json_safe(v) for v in x]
    return str(x)


def run_simulation(
    ticks: int = 3000,
    out_path: str = "results/sim_events.jsonl",
    base_freq: float = 76.4,
    sleep_s: float = 0.0,
    controller: Optional[AmnionController] = None,
) -> str:
    """
    Runs a simulation-only control loop.

    - ticks: number of iterations
    - out_path: JSONL file path
    - base_freq: reference frequency for SensorStub
    - sleep_s: optional sleep between ticks (0 = as fast as possible)
    - controller: optionally pass an existing controller instance
    """
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)

    ctrl = controller or AmnionController()
    sensor = SensorStub(SensorStubConfig(base_freq=base_freq))
    actuator = ActuatorStub()

    t_start = time.time()

    with open(out_path, "w", encoding="utf-8") as f:
        for i in range(int(ticks)):
            sensors: Dict[str, Any] = sensor.read()
            out: Dict[str, Any] = ctrl.step(sensors)
            actuator.apply(out)

            event = {
                "tick": i,
                "ts": time.time(),
                "dt_from_start_s": time.time() - t_start,
                "sensors": sensors,
                "output": out,
                "actuator_last": actuator.get_last(),
            }
            f.write(json.dumps(_json_safe(event), ensure_ascii=False) + "\n")

            if sleep_s and sleep_s > 0:
                time.sleep(float(sleep_s))

    return out_path


if __name__ == "__main__":
    # Minimal CLI run without extra dependencies.
    path = run_simulation(
        ticks=int(os.getenv("AMNION_TICKS", "3000")),
        out_path=os.getenv("AMNION_OUT", "results/sim_events.jsonl"),
        base_freq=float(os.getenv("AMNION_BASE_FREQ", "76.4")),
        sleep_s=float(os.getenv("AMNION_SLEEP_S", "0.0")),
    )
    print(f"OK: wrote {path}")

