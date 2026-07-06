#!/usr/bin/env python3
"""Generate provisional post-FLEX conditional power-quality results."""

from __future__ import annotations
import argparse
from pathlib import Path
import pandas as pd
from drc_power.io import read_powerwatch
from drc_power.quality import conditional_power_quality
from pipeline_common import DEFAULT_OUTPUT_ROOT, DEFAULT_RAW_ROOT, apply_primary_telemetry_window, find_powerwatch, read_config, write_bar_svg


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw-root", type=Path, default=DEFAULT_RAW_ROOT)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    args = parser.parse_args()
    output = args.output_root / "power_quality"
    output.mkdir(parents=True, exist_ok=True)
    canonical = {r["sensor_id"]: r for r in read_config("canonical_powerwatch.csv")}
    rows = []
    for pair in read_config("paired_sensors.csv"):
        sensor = pair["powerwatch_sensor"]
        preference = canonical.get(sensor, {}).get("preferred_version", "original")
        frame = read_powerwatch(find_powerwatch(args.raw_root, sensor, preference))
        frame = apply_primary_telemetry_window(frame, pair["facility_code"])
        rows.append({"facility_code": pair["facility_code"], "sensor_id": sensor,
                     "shared_source": pair["shared_source"],
                     "date_start": frame["time"].min().isoformat(),
                     "date_end": frame["time"].max().isoformat(),
                     **conditional_power_quality(frame),
                     "status": "provisional_full_available_post_sensor_series"})
    sensors = pd.DataFrame(rows).sort_values(["facility_code", "sensor_id"])
    sensors.to_csv(output / "post_flex_conditional_quality_by_sensor.csv", index=False)
    sites = []
    for facility, group in sensors.groupby("facility_code"):
        voltage_den = group["powered_voltage_observations"].sum()
        voltage_num = (group["voltage_quality_pct"] * group["powered_voltage_observations"] / 100).sum()
        freq_den = group["valid_frequency_observations"].sum()
        sites.append({"facility_code": facility, "sensor_count": len(group),
                      "voltage_quality_pct_pooled": voltage_num / voltage_den * 100,
                      "voltage_quality_pct_mean_sensor": group["voltage_quality_pct"].mean(),
                      "status": "provisional_pending_exact_intervention_windows"})
        for tolerance in ("1", "10"):
            column = f"frequency_quality_{tolerance}_pct"
            numerator = (group[column] * group["valid_frequency_observations"] / 100).sum()
            sites[-1][f"{column}_pooled"] = numerator / freq_den * 100
            sites[-1][f"{column}_mean_sensor"] = group[column].mean()
    site_frame = pd.DataFrame(sites).sort_values("facility_code")
    site_frame.to_csv(output / "post_flex_conditional_quality_by_facility.csv", index=False)
    write_bar_svg(output / "post_flex_voltage_quality.svg", site_frame["facility_code"].tolist(),
                  site_frame["voltage_quality_pct_pooled"].tolist(),
                  "Post-FLEX Conditional Voltage Quality (Provisional)", "Voltage compliant while powered (%)")
    print(f"power quality: {len(sensors)} sensors, {len(site_frame)} facilities")


if __name__ == "__main__":
    main()
