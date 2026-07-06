#!/usr/bin/env python3
"""Run all currently implemented reproducible analyses."""

from __future__ import annotations
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    environment = os.environ.copy()
    source_path = str(ROOT / "src")
    environment["PYTHONPATH"] = source_path + os.pathsep + environment.get("PYTHONPATH", "")
    for script in ("run_power_quality.py", "run_reliability.py", "run_energy.py", "run_figure3_summary.py"):
        print(f"\n=== {script} ===", flush=True)
        subprocess.run([sys.executable, str(ROOT / "scripts" / script)], cwd=ROOT, env=environment, check=True)
    print("\nAll analyses completed. Outputs: outputs/generated/")


if __name__ == "__main__":
    main()
