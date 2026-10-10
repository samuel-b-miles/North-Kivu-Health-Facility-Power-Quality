#!/usr/bin/env python3
"""Run all currently implemented reproducible analyses."""

from __future__ import annotations
import argparse
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--from-public", action="store_true", help="Use public DHIS2 panels instead of private exports")
    args = parser.parse_args()
    environment = os.environ.copy()
    source_path = str(ROOT / "src")
    environment["PYTHONPATH"] = source_path + os.pathsep + environment.get("PYTHONPATH", "")
    for script in ("run_power_quality.py", "run_reliability.py", "run_energy.py", "run_baseline_audit.py", "run_longitudinal_pre_audit.py", "run_figure3_summary.py", "run_figure3_timeseries.py", "run_timeline_figure.py", "run_payments.py", "run_health.py", "run_annex.py"):
        print(f"\n=== {script} ===", flush=True)
        command = [sys.executable, str(ROOT / "scripts" / script)]
        if script == "run_health.py" and args.from_public:
            command.append("--from-public")
        subprocess.run(command, cwd=ROOT, env=environment, check=True)
    subprocess.run([sys.executable, str(ROOT / "scripts/run_figure3_summary.py"), "--pqr-policy", "independent"], cwd=ROOT, env=environment, check=True)
    print("\nAll analyses completed. Outputs: outputs/generated/")


if __name__ == "__main__":
    main()
