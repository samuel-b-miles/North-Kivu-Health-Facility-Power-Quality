#!/usr/bin/env python3
"""Verify and extract locally downloaded, Git-ignored release assets."""

from __future__ import annotations

import argparse
import hashlib
import os
import shutil
import tomllib
from pathlib import Path, PureWindowsPath
from zipfile import ZipFile


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = PROJECT_ROOT / "config" / "data_sources.toml"


def digest(path: Path) -> str:
    result = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            result.update(block)
    return result.hexdigest()


def safe_extract(archive: Path, destination: Path) -> int:
    count = 0
    with ZipFile(archive) as source:
        for info in source.infolist():
            # Release archives were created on Windows; normalize separators.
            parts = [part for part in PureWindowsPath(info.filename).parts if part not in ("", ".", "..")]
            target = destination.joinpath(*parts)
            if not target.resolve().is_relative_to(destination.resolve()):
                raise ValueError(f"Unsafe archive path: {info.filename}")
            if info.is_dir():
                target.mkdir(parents=True, exist_ok=True)
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            with source.open(info) as reader, target.open("wb") as writer:
                shutil.copyfileobj(reader, writer, length=1024 * 1024)
            count += 1
    return count


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Verify downloaded DRC release ZIPs and populate local data/raw/."
    )
    parser.add_argument(
        "--source-dir",
        type=Path,
        default=Path(os.environ.get("DRC_DATA_DOWNLOADS", Path.home() / "Downloads")),
        help="Directory containing the three release ZIPs (or set DRC_DATA_DOWNLOADS).",
    )
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--raw-dir", type=Path, default=PROJECT_ROOT / "data" / "raw")
    parser.add_argument("--verify-only", action="store_true")
    parser.add_argument("--force", action="store_true", help="Replace existing extracted asset directories.")
    args = parser.parse_args()

    configuration = tomllib.loads(args.config.read_text(encoding="utf-8"))
    assets = configuration["release"]["assets"]
    verified: list[tuple[dict[str, str], Path]] = []
    for asset in assets:
        source = args.source_dir.expanduser() / asset["filename"]
        if not source.is_file():
            raise FileNotFoundError(f"Missing release asset: {source}")
        actual = digest(source)
        if actual != asset["sha256"]:
            raise ValueError(
                f"Checksum mismatch for {source.name}: expected {asset['sha256']}, got {actual}"
            )
        verified.append((asset, source))
        print(f"verified  {source.name}")

    if args.verify_only:
        return

    downloads = args.raw_dir / "downloads"
    extracted = args.raw_dir / "extracted"
    downloads.mkdir(parents=True, exist_ok=True)
    extracted.mkdir(parents=True, exist_ok=True)
    for asset, source in verified:
        local_archive = downloads / source.name
        if local_archive.resolve() != source.resolve():
            shutil.copy2(source, local_archive)
        destination = extracted / source.stem
        if destination.exists() and args.force:
            shutil.rmtree(destination)
        if destination.exists():
            print(f"existing  {destination} (use --force to replace)")
            continue
        destination.mkdir(parents=True)
        count = safe_extract(local_archive, destination)
        print(f"extracted {source.name}: {count} files")


if __name__ == "__main__":
    main()

