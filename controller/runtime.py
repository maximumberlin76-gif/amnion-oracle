from dataclasses import dataclass
from time import time


@dataclass
class RuntimeState:
    ts: float
    cycle: int
    phase_avg: float
    coherence_avg: float
    last_ok: bool
    note: str = ""


def now_ts() -> float:
    return float(time())
