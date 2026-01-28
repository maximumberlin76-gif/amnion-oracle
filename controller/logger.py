from __future__ import annotations

import json
import sys
import time
from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class Logger:
    """
    Tiny logger for AMNION controller.
    Emits JSON lines to stdout/stderr.
    """

    name: str = "amnion"
    to_stderr: bool = False

    def _emit(self, level: str, event: str, data: Optional[Dict[str, Any]] = None, ts: float = 0.0) -> None:
        if ts == 0.0:
            ts = time.time()

        payload: Dict[str, Any] = {
            "ts": ts,
            "name": self.name,
            "level": level,
            "event": event,
        }
        if data:
            payload["data"] = data

        line = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
        stream = sys.stderr if self.to_stderr else sys.stdout
        stream.write(line + "\n")
        stream.flush()

    def info(self, event: str, data: Optional[Dict[str, Any]] = None, ts: float = 0.0) -> None:
        self._emit("INFO", event, data, ts)

    def warn(self, event: str, data: Optional[Dict[str, Any]] = None, ts: float = 0.0) -> None:
        self._emit("WARN", event, data, ts)

    def error(self, event: str, data: Optional[Dict[str, Any]] = None, ts: float = 0.0) -> None:
        self._emit("ERROR", event, data, ts)
