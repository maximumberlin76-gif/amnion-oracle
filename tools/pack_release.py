from __future__ import annotations

import argparse
import hashlib
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Tuple


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def collect_files(root: Path, include: List[str]) -> List[Path]:
    files: List[Path] = []
    for pattern in include:
        files.extend(root.glob(pattern))
    # normalize + unique + only files
    uniq = sorted({p.resolve() for p in files if p.is_file()})
    return uniq


def make_manifest(files: List[Path], root: Path) -> List[Tuple[str, str]]:
    manifest: List[Tuple[str, str]] = []
    for p in files:
        rel = str(p.relative_to(root)).replace("\\", "/")
        manifest.append((rel, sha256_file(p)))
    return manifest


def write_manifest_txt(manifest: List[Tuple[str, str]], out_path: Path) -> None:
    # format: "<sha256>  <path>"
    lines = [f"{digest}  {rel}" for rel, digest in manifest]
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_zip(zip_path: Path, root: Path, files: List[Path], manifest_path: Path) -> None:
    zip_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        # add payload files
        for p in files:
            arcname = str(p.relative_to(root)).replace("\\", "/")
            zf.write(p, arcname=arcname)
        # add manifest
        zf.write(manifest_path, arcname=manifest_path.name)


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Pack AMNION release ZIP with SHA-256 manifest.")
    parser.add_argument("--root", default=".", help="Repo root (default: .)")
    parser.add_argument("--out", default="dist/amnion_release.zip", help="Output zip path")
    parser.add_argument(
        "--include",
        nargs="+",
        default=[
            "README.md",
            "pyproject.toml",
            "amnion_oracle/**/*.py",
            "controller/**/*.py",
            "tools/**/*.py",
            "tests/**/*.py",
        ],
        help="Glob patterns to include",
    )

    args = parser.parse_args(argv)
    root = Path(args.root).resolve()
    out_zip = (root / args.out).resolve()

    files = collect_files(root, args.include)

    ts = datetime.now(timezone.utc).isoformat()
    manifest = make_manifest(files, root)

    dist_dir = out_zip.parent
    dist_dir.mkdir(parents=True, exist_ok=True)

    manifest_path = dist_dir / "sha256sum.txt"
    write_manifest_txt(manifest, manifest_path)

    build_zip(out_zip, root, files, manifest_path)

    print(f"[pack_release] utc={ts}")
    print(f"[pack_release] files={len(files)}")
    print(f"[pack_release] manifest={manifest_path}")
    print(f"[pack_release] zip={out_zip}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
