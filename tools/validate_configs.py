#!/usr/bin/env python3
import argparse
import json
from pathlib import Path

import yaml
from jsonschema import Draft7Validator


ROOT = Path(__file__).resolve().parents[1]


def load_yaml(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if data is None:
        data = {}
    if not isinstance(data, dict):
        raise ValueError(f"YAML must be a mapping (dict): {path}")
    return data


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def validate_one(config_path: Path, schema_path: Path) -> list[str]:
    cfg = load_yaml(config_path)
    schema = load_json(schema_path)

    v = Draft7Validator(schema)
    errors = sorted(v.iter_errors(cfg), key=lambda e: e.path)

    out = []
    for e in errors:
        loc = ".".join([str(x) for x in e.path]) if e.path else "(root)"
        out.append(f"{config_path.name}: {loc}: {e.message}")
    return out


def main():
    p = argparse.ArgumentParser(description="Validate AMNION-ORACLE YAML configs against JSON Schemas.")
    p.add_argument("--configs", default="configs", help="Path to configs folder (default: configs)")
    p.add_argument("--schemas", default="schemas", help="Path to schemas folder (default: schemas)")
    p.add_argument("--all", action="store_true", help="Validate all known configs")
    args = p.parse_args()

    configs_dir = (ROOT / args.configs).resolve()
    schemas_dir = (ROOT / args.schemas).resolve()

    mapping = {
        "00_system.yaml": "system.schema.json",
        "01_interfaces.yaml": "interfaces.schema.json",
        "02_safety.yaml": "safety.schema.json",
        "03_metrics.yaml": "metrics.schema.json",
        "04_logging.yaml": "logging.schema.json",
        "05_profile.yaml": "profile.schema.json",
    }

    if not configs_dir.exists():
        raise SystemExit(f"Configs folder not found: {configs_dir}")
    if not schemas_dir.exists():
        raise SystemExit(f"Schemas folder not found: {schemas_dir}")

    errors_all: list[str] = []

    if args.all:
        for cfg_name, schema_name in mapping.items():
            cfg_path = configs_dir / cfg_name
            schema_path = schemas_dir / schema_name

            if not cfg_path.exists():
                continue
            if not schema_path.exists():
                errors_all.append(f"Missing schema: {schema_name}")
                continue

            errors_all.extend(validate_one(cfg_path, schema_path))
    else:
        for cfg_name, schema_name in mapping.items():
            cfg_path = configs_dir / cfg_name
            schema_path = schemas_dir / schema_name
            if cfg_path.exists() and schema_path.exists():
                errors_all.extend(validate_one(cfg_path, schema_path))

    if errors_all:
        print("CONFIG VALIDATION: FAILED")
        for line in errors_all:
            print(" -", line)
        raise SystemExit(2)

    print("CONFIG VALIDATION: OK")
    raise SystemExit(0)


if __name__ == "__main__":
    main()
  
