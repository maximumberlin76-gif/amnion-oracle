from __future__ import annotations

import json
import time
from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class Logger:
    name: str = "amnion"

    def _emit(
        self,
        level: str,
        event: str,
        data: Optional[Dict[str, Any]] = None,
        ts: float = 0.0,
    ) -> None:
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

        print(json.dumps(payload, ensure_ascii=False))

    def info(self, event: str, data: Optional[Dict[str, Any]] = None) -> None:
        self._emit("INFO", event, data)

    def warn(self, event: str, data: Optional[Dict[str, Any]] = None) -> None:
        self._emit("WARN", event, data)

    def error(self, event: str, data: Optional[Dict[str, Any]] = None) -> None:
        self._emit("ERROR", event, data)
