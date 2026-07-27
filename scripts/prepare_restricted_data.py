#!/usr/bin/env python3
"""Copy, verify, and extract authorized restricted inputs for reproduction."""

from __future__ import annotations

import argparse
import csv
import hashlib
import shutil
from pathlib import Path, PureWindowsPath
from zipfile import ZipFile


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MANIFEST = PROJECT_ROOT / "config" / "restricted_data_sources.csv"


def digest(path: Path) -> str:
    result = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            result.update(block)
    return result.hexdigest()


def safe_extract(archive: Path, destination: Path, force: bool = False) -> int:
    if destination.exists() and force:
        shutil.rmtree(destination)
    if destination.exists():
        return 0
    destination.mkdir(parents=True)
    count = 0
    with ZipFile(archive) as source:
        for info in source.infolist():
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


def read_manifest() -> list[dict[str, str]]:
    with MANIFEST.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def locate_source(source_root: Path, row: dict[str, str]) -> Path:
    canonical = source_root / row["source_path"]
    if canonical.is_file():
        return canonical
    matches = list(source_root.rglob(Path(row["source_path"]).name))
    if len(matches) == 1:
        return matches[0]
    if not matches:
        raise FileNotFoundError(f"Missing {row['dataset_id']}: expected {canonical}")
    raise FileNotFoundError(f"Multiple candidates for {row['dataset_id']}; use canonical layout")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Prepare authorized restricted data for local reproduction."
    )
    parser.add_argument(
        "--source",
        type=Path,
        required=True,
        help="Restricted data bundle/repository root, or a folder containing the required files.",
    )
    parser.add_argument("--verify-only", action="store_true", help="Verify source checksums without copying.")
    parser.add_argument("--force", action="store_true", help="Replace existing local files/extracted folders.")
    args = parser.parse_args()

    source_root = args.source.expanduser().resolve()
    if not source_root.exists():
        raise FileNotFoundError(source_root)

    verified: list[tuple[dict[str, str], Path]] = []
    for row in read_manifest():
        source = locate_source(source_root, row)
        actual = digest(source)
        if actual != row["sha256"]:
            raise ValueError(
                f"Checksum mismatch for {row['dataset_id']}: expected {row['sha256']}, got {actual}"
            )
        print(f"verified  {row['dataset_id']}  {source}")
        verified.append((row, source))

    if args.verify_only:
        return

    for row, source in verified:
        destination = PROJECT_ROOT / row["local_destination"]
        if destination.exists() and not args.force:
            print(f"existing  {destination} (use --force to replace)")
        else:
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
            print(f"copied    {destination}")

        if destination.suffix.lower() == ".zip":
            extracted = PROJECT_ROOT / "data" / "raw" / "extracted" / destination.stem
            count = safe_extract(destination, extracted, force=args.force)
            if count:
                print(f"extracted {destination.name}: {count} files")
            else:
                print(f"existing  {extracted} (use --force to replace)")

    print("Restricted inputs are ready. Run: python scripts/run_all.py")


if __name__ == "__main__":
    main()
