#!/usr/bin/env python3
"""
AMNION-ORACLE — Release Packager

Purpose:
- Build a deterministic release bundle (zip) for the repository.
- Include only relevant folders/files.
- Exclude junk: venv, caches, .git, etc.

Usage:
python tools/pack_release.py --out dist
python tools/pack_release.py --out dist --name amnion-oracle --version 0.1.0
"""

from __future__ import annotations

import argparse
import hashlib
import os
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, List, Tuple


INCLUDE_DEFAULT = [
    "controller",
    "schemas",
    "tools",
    "examples",
    "tests",
    "README.md",
    "LICENSE",
]


EXCLUDE_DIR_NAMES = {
    ".git",
    ".github",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".venv",
    "venv",
    "env",
    "dist",
    "build",
    ".idea",
    ".vscode",
    "node_modules",
}

EXCLUDE_FILE_SUFFIXES = {
    ".pyc",
    ".pyo",
    ".log",
    ".tmp",
}

EXCLUDE_FILE_NAMES = {
    ".DS_Store",
    "Thumbs.db",
}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def repo_root() -> Path:
    # tools/pack_release.py -> repo root
    return Path(__file__).resolve().parents[1]


def should_exclude_path(p: Path) -> bool:
    # Directory name exclusions
    for part in p.parts:
        if part in EXCLUDE_DIR_NAMES:
            return True

    # File name/suffix exclusions
    if p.is_file():
        if p.name in EXCLUDE_FILE_NAMES:
            return True
        if p.suffix.lower() in EXCLUDE_FILE_SUFFIXES:
            return True

    return False


def iter_included_paths(root: Path, includes: List[str]) -> List[Path]:
    paths: List[Path] = []
    for inc in includes:
        target = root / inc
        if not target.exists():
            # Missing items are simply ignored to keep packer flexible
            continue

        if target.is_file():
            if not should_exclude_path(target):
                paths.append(target)
        else:
            # walk directory
            for sub in target.rglob("*"):
                if sub.is_dir():
                    continue
                if should_exclude_path(sub):
                    continue
                paths.append(sub)

    # Make deterministic order
    paths_sorted = sorted(set(paths), key=lambda x: str(x.as_posix()))
    return paths_sorted


def zip_write_deterministic(zipf: zipfile.ZipFile, src: Path, arcname: str) -> None:
    # Use fixed timestamp to make zip stable across builds
    info = zipfile.ZipInfo(arcname)
    info.date_time = (1980, 1, 1, 0, 0, 0)  # earliest allowed
    info.compress_type = zipfile.ZIP_DEFLATED

    # Preserve *basic* file permission bits if possible
    try:
        mode = src.stat().st_mode
        info.external_attr = (mode & 0xFFFF) << 16
    except Exception:
        pass

    with src.open("rb") as f:
        data = f.read()
    zipf.writestr(info, data)


def build_manifest(entries: List[Tuple[str, str]]) -> str:
    # entries: [(relative_path, sha256)]
    now = datetime.now(timezone.utc).isoformat()
    lines = []
    lines.append("# AMNION-ORACLE — Release Manifest")
    lines.append(f"# Generated (UTC): {now}")
    lines.append("")
    lines.append("files:")
    for rel, digest in entries:
        lines.append(f"  - path: {rel}")
        lines.append(f"    sha256: {digest}")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="dist", help="Output directory for release bundle")
    ap.add_argument("--name", default="amnion-oracle", help="Bundle base name")
    ap.add_argument("--version", default=None, help="Version string (optional)")
    ap.add_argument(
        "--include",
        action="append",
        default=[],
        help="Extra include paths (repeatable). Example: --include CHANGELOG.md",
    )
    args = ap.parse_args()

    root = repo_root()
    out_dir = (root / args.out).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    includes = INCLUDE_DEFAULT + list(args.include)

    paths = iter_included_paths(root, includes)
    if not paths:
        print("Nothing to package. Check include paths.", file=sys.stderr)
        return 2

    version_tag = f"-{args.version}" if args.version else ""
    zip_name = f"{args.name}{version_tag}.zip"
    zip_path = out_dir / zip_name

    manifest_entries: List[Tuple[str, str]] = []

    # Create zip deterministically
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zipf:
        for p in paths:
            rel = p.relative_to(root).as_posix()
            digest = sha256_file(p)
            manifest_entries.append((rel, digest))
            zip_write_deterministic(zipf, p, rel)

        # Add manifest inside zip
        manifest_text = build_manifest(manifest_entries)
        info = zipfile.ZipInfo("MANIFEST.yml")
        info.date_time = (1980, 1, 1, 0, 0, 0)
        info.compress_type = zipfile.ZIP_DEFLATED
        zipf.writestr(info, manifest_text.encode("utf-8"))

    # Also save external manifest
    manifest_path = out_dir / "MANIFEST.yml"
    manifest_path.write_text(build_manifest(manifest_entries), encoding="utf-8")

    # Print final digests
    zip_digest = sha256_file(zip_path)
    print(f"Release bundle: {zip_path}")
    print(f"Bundle sha256:  {zip_digest}")
    print(f"Manifest:       {manifest_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
  
