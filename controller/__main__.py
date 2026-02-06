# controller/__main__.py
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict

from controller.config_loader import load_config
from controller.amnion_controller import AmnionController


def _demo_sensors(cfg: Dict[str, Any]) -> Dict[str, Any]:
    # Minimal demo frame: match keys from configs/01_interfaces.yaml
    return {
        "phase": 0.0,
        "coherence": 0.95,
        "power_in": 10.0,
        "power_draw": 5.0,
        "desired_u": 0.5,
        "emergency_stop": False,
    }


def main() -> int:
    ap = argparse.ArgumentParser(prog="amnion-oracle")
    ap.add_argument("--config-dir", default="configs", help="Path to configs/ folder")
    ap.add_argument("--ticks", type=int, default=3, help="How many demo ticks to run")
    args = ap.parse_args()

    cfg_dir = Path(args.config_dir)
    loaded = load_config(config_dir=cfg_dir)
    cfg = loaded.data  # merged

    c = AmnionController()

    for i in range(max(1, int(args.ticks))):
        sensors = _demo_sensors(cfg)
        out = c.step(sensors)
        print(json.dumps({"tick": i + 1, "output": out}, ensure_ascii=False))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
