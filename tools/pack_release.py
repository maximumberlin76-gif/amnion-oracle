#!/usr/bin/env python3
"""
AMNION release packer (canonical).

Creates a release ZIP with:
- source snapshot (selected folders/files)
- SHA256 manifest
- minimal metadata (timestamp, git sha if available)

Usage:
  python tools/pack_release.py --out dist/amnion_oracle_release.zip
  python tools/pack_release.py --out dist/amnion_oracle_release.zip --include docs schemas configs controller amnion_oracle tools tests README.md LICENSE
"""

from __future__ import annotations

import argparse
import hashlib
import os
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable
from zipfile import ZIP_DEFLATED, ZipFile


DEFAULT_INCLUDE = [
    "amnion_oracle",
    "controller",
    "configs",
    "schemas",
    "tools",
    "tests",
    "docs",
    "README.md",
    "LICENSE",
    "pyproject.toml",
    "requirements.txt",
    "requirements-dev.txt",
]


@dataclass(frozen=True)
class Item:
    path: Path
    arcname: str  # path inside zip


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def git_sha() -> str:
    try:
        out = subprocess.check_output(["git", "rev-parse", "HEAD"], stderr=subprocess.DEVNULL, text=True).strip()
        if out:
            return out
    except Exception:
        pass
    return "unknown"


def iter_files(root: Path, include: Iterable[str]) -> list[Item]:
    items: list[Item] = []
    for entry in include:
        p = (root / entry).resolve()
        if not p.exists():
            continue

        if p.is_file():
            items.append(Item(path=p, arcname=str(p.relative_to(root)).replace("\\", "/")))
            continue

        # directory
        for fp in p.rglob("*"):
            if fp.is_dir():
                continue
            # skip common junk
            name = fp.name
            if name.endswith((".pyc", ".pyo")):
                continue
            if name == ".DS_Store":
                continue
            if "__pycache__" in fp.parts:
                continue
            if ".pytest_cache" in fp.parts:
                continue
            if ".ruff_cache" in fp.parts:
                continue
            rel = fp.relative_to(root)
            items.append(Item(path=fp, arcname=str(rel).replace("\\", "/")))
    # stable order
    items.sort(key=lambda x: x.arcname)
    return items


def write_manifest(root: Path, items: list[Item], ts_iso: str, sha: str) -> str:
    lines: list[str] = []
    lines.append("AMNION Release Manifest v1")
    lines.append(f"timestamp_utc: {ts_iso}")
    lines.append(f"git_sha: {sha}")
    lines.append("")
    lines.append("sha256  path")
    for it in items:
        digest = sha256_file(it.path)
        lines.append(f"{digest}  {it.arcname}")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True, help="Output zip path, e.g. dist/release.zip")
    ap.add_argument(
        "--include",
        nargs="*",
        default=DEFAULT_INCLUDE,
        help="Paths to include (files/dirs) relative to repo root",
    )
    args = ap.parse_args()

    root = Path(__file__).resolve().parents[1]
    out_path = Path(args.out).expanduser().resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)

    ts_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    sha = git_sha()

    items = iter_files(root, args.include)
    if not items:
        print("Nothing to pack (no include paths found).", file=sys.stderr)
        return 2

    manifest_text = write_manifest(root, items, ts_iso, sha)

    # write zip
    with ZipFile(out_path, "w", compression=ZIP_DEFLATED) as zf:
        # metadata
        zf.writestr("RELEASE_META.txt", f"timestamp_utc: {ts_iso}\ngit_sha: {sha}\n")
        zf.writestr("MANIFEST_SHA256.txt", manifest_text)
        # files
        for it in items:
            zf.write(it.path, it.arcname)

    print(f"OK: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
