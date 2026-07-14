#!/usr/bin/env python3
"""Generate facility and fleet HOP-metered energy tables and figures."""

from __future__ import annotations
import argparse
from pathlib import Path
import pandas as pd
from drc_power.energy import aggregate_daily_energy, parse_energy_wh
from pipeline_common import DEFAULT_OUTPUT_ROOT, DEFAULT_RAW_ROOT, find_hop_energy, read_config, write_monthly_facility_panels_svg, write_stacked_svg, write_value_bar_svg


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
                               "positive_days": int((parsed > 0).sum()), "analysis_group": row["analysis_group"],
                               "status": row["status"]})
        facility_frames[facility] = aggregate_daily_energy(frames)[["facility_total_kwh"]].rename(
            columns={"facility_total_kwh": facility})
    meter_summary = pd.DataFrame(meter_rows); meter_summary.to_csv(output / "energy_by_meter.csv", index=False)
    facility_summary = meter_summary.groupby("facility_code", as_index=False).agg(
        total_installed_system_consumption_kwh=("total_kwh", "sum"),
        included_meters=("sensor_id", "count"),
    ).sort_values("facility_code")
    core = meter_summary[meter_summary["analysis_group"] == "critical_core"].groupby("facility_code")["total_kwh"].sum()
    morgue = meter_summary[meter_summary["analysis_group"] == "supplemental_morgue"].groupby("facility_code")["total_kwh"].sum()
    facility_summary["critical_core_consumption_kwh"] = facility_summary["facility_code"].map(core).fillna(0)
    facility_summary["supplemental_morgue_consumption_kwh"] = facility_summary["facility_code"].map(morgue).fillna(0)
    facility_summary["fleet_share_pct"] = (
        facility_summary["total_installed_system_consumption_kwh"] /
        facility_summary["total_installed_system_consumption_kwh"].sum() * 100
    )
    facility_summary["status"] = "provisional_pending_topology_and_active-window_review"
    facility_summary.to_csv(output / "total_consumption_by_facility.csv", index=False)
    daily = pd.concat(facility_frames.values(), axis=1).sort_index()
    daily.index = pd.to_datetime(daily.index, errors="raise", utc=True)
    daily.to_csv(output / "daily_energy_by_facility.csv")
    monthly = daily.resample("MS").sum(min_count=1)
    # Figure 4 is meant to compare complete calendar months. Drop the final
    # month when the raw daily export ends before that month is complete, rather
    # than showing a misleading short bar for a partial final month.
    final_day = daily.index.max().normalize()
    final_month_start = final_day.replace(day=1)
    final_month_end = final_month_start + pd.offsets.MonthEnd(0)
    if final_day < final_month_end:
        monthly = monthly[monthly.index < final_month_start]
    monthly.to_csv(output / "monthly_energy_by_facility.csv")
    telemetry_exclusions = [r for r in read_config("analysis_periods.csv") if r["period_type"] == "telemetry_exclusion"]
    write_monthly_facility_panels_svg(output / "monthly_energy_six_panel.svg", monthly, telemetry_exclusions)
    write_monthly_facility_panels_svg(output / "figure4_monthly_energy_six_panel.svg", monthly, telemetry_exclusions)
    cumulative = daily.fillna(0).cumsum(); cumulative.to_csv(output / "cumulative_energy_by_facility.csv")
    write_stacked_svg(output / "fleet_cumulative_energy.svg", cumulative,
                      "Fleet Cumulative FLEX Energy (Provisional Topology)")
    write_value_bar_svg(output / "total_consumption_by_facility.svg",
                        facility_summary["facility_code"].tolist(),
                        facility_summary["total_installed_system_consumption_kwh"].tolist(),
                        "Total HOP-Metered FLEX Consumption by Facility (Provisional)",
                        "Total consumption (kWh)")
    write_value_bar_svg(output / "critical_core_consumption_by_facility.svg",
                        facility_summary["facility_code"].tolist(),
                        facility_summary["critical_core_consumption_kwh"].tolist(),
                        "Critical-Circuit HOP Consumption by Facility (Provisional)",
                        "Critical-circuit consumption (kWh)")
    print(f"energy: {len(meter_summary)} meters, {len(facility_frames)} facilities")


if __name__ == "__main__":
    main()
