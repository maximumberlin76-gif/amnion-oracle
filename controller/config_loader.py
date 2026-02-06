# controller/config_loader.py
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml


DEFAULT_CONFIG_DIR = Path(__file__).resolve().parent.parent / "configs"

DEFAULT_CONFIG_FILES = [
    "00_system.yaml",
    "01_interfaces.yaml",
    "02_safety.yaml",
    "03_metrics.yaml",
    "04_logging.yaml",
    "05_profile.yaml",
    "06_safeguards.yaml",
]


class ConfigError(Exception):
    """Fatal configuration error."""


def _read_yaml(path: Path) -> Dict[str, Any]:
    if not path.exists():
        raise ConfigError(f"Config file not found: {path}")
    try:
        with path.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        if not isinstance(data, dict):
            raise ConfigError(f"YAML root must be a mapping/dict: {path}")
        return data
    except yaml.YAMLError as e:
        raise ConfigError(f"YAML parse error in {path}: {e}") from e


def _deep_merge(base: Dict[str, Any], patch: Dict[str, Any]) -> Dict[str, Any]:
    """
    Deep merge dicts:
    - dict + dict -> merge recursively
    - otherwise patch overrides base
    """
    out = dict(base)
    for k, v in patch.items():
        if k in out and isinstance(out[k], dict) and isinstance(v, dict):
            out[k] = _deep_merge(out[k], v)
        else:
            out[k] = v
    return out


def _validate_basic(cfg: Dict[str, Any]) -> None:
    # Minimal sanity checks (без фанатизма)
    if "version" not in cfg:
        cfg["version"] = "0.1"

    # Optional guardrails
    # Ensure blocks exist
    cfg.setdefault("system", {})
    cfg.setdefault("interfaces", {})
    cfg.setdefault("safety", {})
    cfg.setdefault("metrics", {})
    cfg.setdefault("logging", {})
    cfg.setdefault("profile", {})
    cfg.setdefault("safeguards", {})


@dataclass(frozen=True)
class LoadedConfig:
    config_dir: Path
    files: List[str]
    data: Dict[str, Any]


def load_config(
    config_dir: Optional[Path] = None,
    files: Optional[List[str]] = None,
) -> LoadedConfig:
    """
    Load AMNION-ORACLE configuration from YAML files in /configs.
    Returns merged dict + metadata.
    """
    cfg_dir = (config_dir or DEFAULT_CONFIG_DIR).resolve()
    cfg_files = files or DEFAULT_CONFIG_FILES

    merged: Dict[str, Any] = {}
    used_files: List[str] = []

    for name in cfg_files:
        p = cfg_dir / name
        part = _read_yaml(p)
        merged = _deep_merge(merged, part)
        used_files.append(name)

    _validate_basic(merged)

    return LoadedConfig(
        config_dir=cfg_dir,
        files=used_files,
        data=merged,
    )


def load_manifest(config_dir: Optional[Path] = None) -> Dict[str, Any]:
    """
    Optional: read configs/manifest.yaml if present.
    Not fatal if missing.
    """
    cfg_dir = (config_dir or DEFAULT_CONFIG_DIR).resolve()
    p = cfg_dir / "manifest.yaml"
    if not p.exists():
        return {}
    data = _read_yaml(p)
    return data
