#!/usr/bin/env python3
"""Generate provisional paired-sensor confirmed reliability results."""

from __future__ import annotations
import argparse
from pathlib import Path
import pandas as pd
from drc_power.io import read_hop_voltage, read_powerwatch
from drc_power.reliability import paired_reliability
from pipeline_common import DEFAULT_OUTPUT_ROOT, DEFAULT_RAW_ROOT, find_hop_voltage, find_powerwatch, read_config, write_bar_svg


def main() -> None:
    parser = argparse.ArgumentParser(); parser.add_argument("--raw-root", type=Path, default=DEFAULT_RAW_ROOT)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT); args = parser.parse_args()
    output = args.output_root / "reliability"; output.mkdir(parents=True, exist_ok=True)
    canonical = {r["sensor_id"]: r for r in read_config("canonical_powerwatch.csv")}; rows = []
    for pair in read_config("paired_sensors.csv"):
        pw_sensor = pair["powerwatch_sensor"]; preferred = canonical.get(pw_sensor, {}).get("preferred_version", "original")
        hop = read_hop_voltage(find_hop_voltage(args.raw_root, pair["hop_sensor"]))
        pw = read_powerwatch(find_powerwatch(args.raw_root, pw_sensor, preferred))
        rows.append({**pair, **paired_reliability(hop, pw),
                     "status": "provisional_pending_alignment_and_exclusion_review"})
    results = pd.DataFrame(rows).sort_values(["facility_code", "hop_sensor"])
    results.to_csv(output / "paired_confirmed_reliability.csv", index=False)
    labels = (results["facility_code"] + " " + results["shared_source"]).tolist()
    write_bar_svg(output / "paired_confirmed_availability.svg", labels,
                  results["availability_among_assessed_concordant_intervals_pct"].tolist(),
                  "Availability Among Assessed Concordant Intervals (Provisional)",
                  "Availability among assessed intervals (%)")
    print(f"reliability: {len(results)} paired circuits")


if __name__ == "__main__":
    main()
