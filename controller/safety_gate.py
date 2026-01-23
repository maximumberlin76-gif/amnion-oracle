# controller/safety_gate.py
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class SafetyGateConfig:
    """
    Default config is intentionally permissive but SAFE.
    Tests expect SafetyGate() to work without arguments.
    """
    # Allowed inclusive range for "blocks" / "indexes"
    min_block: int = 0
    max_block: int = 10_000

    # Optional policy toggles
    strict: bool = True


class NullLogger:
    def info(self, *args: Any, **kwargs: Any) -> None:
        pass

    def warning(self, *args: Any, **kwargs: Any) -> None:
        pass

    def error(self, *args: Any, **kwargs: Any) -> None:
        pass


class SafetyGate:
    """
    Small validation gate used by tests.

    IMPORTANT:
    - Must be constructible as SafetyGate() (no required args).
    - Must provide block/index range validation.
    """

    def __init__(self, cfg: Optional[Dict[str, Any]] = None, log: Optional[Any] = None):
        # cfg can be dict or SafetyGateConfig-like
        self.log = log if log is not None else NullLogger()

        if cfg is None:
            self.cfg = SafetyGateConfig()
        elif isinstance(cfg, SafetyGateConfig):
            self.cfg = cfg
        elif isinstance(cfg, dict):
            self.cfg = SafetyGateConfig(
                min_block=int(cfg.get("min_block", 0)),
                max_block=int(cfg.get("max_block", 10_000)),
                strict=bool(cfg.get("strict", True)),
            )
        else:
            # fallback: accept anything with attributes
            self.cfg = SafetyGateConfig(
                min_block=int(getattr(cfg, "min_block", 0)),
                max_block=int(getattr(cfg, "max_block", 10_000)),
                strict=bool(getattr(cfg, "strict", True)),
            )

    # ---------- core checks ----------

    def is_block_in_range(self, block: int) -> bool:
        return self.cfg.min_block <= int(block) <= self.cfg.max_block

    def validate_blocks(self, blocks: List[int]) -> Tuple[bool, List[int]]:
        """
        Returns: (ok, out_of_range_blocks)
        """
        out = [int(b) for b in blocks if not self.is_block_in_range(int(b))]
        return (len(out) == 0, out)

    def assert_blocks(self, blocks: List[int]) -> None:
        ok, out = self.validate_blocks(blocks)
        if not ok:
            msg = f"Blocks out of range: {out} (allowed {self.cfg.min_block}..{self.cfg.max_block})"
            self.log.error(msg)
            raise ValueError(msg)

    # ---------- convenience API for controller/tests ----------

    def guard(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generic guard. Accepts payload containing:
          - "blocks": list[int] or single int
        Returns payload with diagnostic status.
        """
        blocks = payload.get("blocks", [])
        if isinstance(blocks, int):
            blocks = [blocks]
        blocks = [int(b) for b in (blocks or [])]

        ok, out = self.validate_blocks(blocks)
        result = dict(payload)
        result["safety_ok"] = ok
        result["blocks_out_of_range"] = out

        if self.cfg.strict and not ok:
            self.assert_blocks(blocks)

        return result
      
