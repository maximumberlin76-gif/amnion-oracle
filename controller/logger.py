import json
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Any, Dict, Optional


@dataclass
class LogEvent:
    ts: float
    level: str
    event: str
    data: Dict[str, Any]


class JsonLogger:
    """
    Минимальный JSON-логгер без зависимостей.
    Пишет одну JSON-строку на событие.
    """
    def __init__(self, stream=None, component: str = "controller"):
        self.stream = stream
        self.component = component

    def _emit(self, level: str, event: str, data: Optional[Dict[str, Any]] = None, ts: float = 0.0):
        if data is None:
            data = {}
        payload = {
            "ts": ts,
            "iso": datetime.utcfromtimestamp(ts).isoformat() + "Z",
            "level": level,
            "component": self.component,
            "event": event,
            "data": data,
        }
        line = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
        if self.stream is None:
            print(line)
        else:
            self.stream.write(line + "\n")
            self.stream.flush()

    def info(self, event: str, data: Optional[Dict[str, Any]] = None, ts: float = 0.0):
        self._emit("INFO", event, data, ts)

    def warn(self, event: str, data: Optional[Dict[str, Any]] = None, ts: float = 0.0):
             
