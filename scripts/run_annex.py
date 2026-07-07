#!/usr/bin/env python3
"""Generate all annex-ready tables from current repository outputs."""

from pathlib import Path
from drc_power.annex import build_annex_tables
from pipeline_common import DEFAULT_OUTPUT_ROOT, PROJECT_ROOT


def main() -> None:
    paths = build_annex_tables(
        DEFAULT_OUTPUT_ROOT,
        PROJECT_ROOT / "config",
        DEFAULT_OUTPUT_ROOT / "annex",
    )
    for path in paths.values():
        print(path.relative_to(PROJECT_ROOT))


if __name__ == "__main__":
    main()
