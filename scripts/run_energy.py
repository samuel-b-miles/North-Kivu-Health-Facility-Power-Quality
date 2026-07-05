#!/usr/bin/env python3
"""Generate fleet cumulative FLEX energy tables and figure."""

from __future__ import annotations
import argparse
from pathlib import Path
import pandas as pd
from drc_power.energy import aggregate_daily_energy, parse_energy_wh
from pipeline_common import DEFAULT_OUTPUT_ROOT, DEFAULT_RAW_ROOT, find_hop_energy, read_config, write_stacked_svg


def read_active_energy(path: Path) -> pd.DataFrame:
    frame = pd.read_csv(path); values = frame["Energy per Day"].map(parse_energy_wh)
    positive = values > 0
    if positive.any():
        frame.loc[frame.index < positive.idxmax(), "Energy per Day"] = pd.NA
    return frame


def main() -> None:
    parser = argparse.ArgumentParser(); parser.add_argument("--raw-root", type=Path, default=DEFAULT_RAW_ROOT)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT); args = parser.parse_args()
    output = args.output_root / "energy"; output.mkdir(parents=True, exist_ok=True)
    meters = [r for r in read_config("energy_meters.csv") if r["include"].lower() == "true"]
    facility_frames = {}; meter_rows = []
    for facility in sorted({row["facility_code"] for row in meters}):
        frames = {}
        for row in [r for r in meters if r["facility_code"] == facility]:
            frame = read_active_energy(find_hop_energy(args.raw_root, row["sensor_id"])); frames[row["sensor_id"]] = frame
            parsed = frame["Energy per Day"].map(parse_energy_wh) / 1000
            meter_rows.append({"facility_code": facility, "sensor_id": row["sensor_id"], "load": row["load"],
                               "total_kwh": parsed.sum(min_count=1), "reporting_days": int(parsed.notna().sum()),
                               "positive_days": int((parsed > 0).sum()), "status": row["status"]})
        facility_frames[facility] = aggregate_daily_energy(frames)[["facility_total_kwh"]].rename(
            columns={"facility_total_kwh": facility})
    meter_summary = pd.DataFrame(meter_rows); meter_summary.to_csv(output / "energy_by_meter.csv", index=False)
    daily = pd.concat(facility_frames.values(), axis=1).sort_index(); daily.to_csv(output / "daily_energy_by_facility.csv")
    cumulative = daily.fillna(0).cumsum(); cumulative.to_csv(output / "cumulative_energy_by_facility.csv")
    write_stacked_svg(output / "fleet_cumulative_energy.svg", cumulative,
                      "Fleet Cumulative FLEX Energy (Provisional Topology)")
    print(f"energy: {len(meter_summary)} meters, {len(facility_frames)} facilities")


if __name__ == "__main__":
    main()
