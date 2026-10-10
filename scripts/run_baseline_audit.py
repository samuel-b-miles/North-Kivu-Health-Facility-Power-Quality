#!/usr/bin/env python3
"""Reconstruct short-source comparisons without treating them as verified baselines."""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

import pandas as pd

from drc_power.io import read_hop_voltage, read_powerwatch
from drc_power.monitoring_audit import monitoring_summary
from drc_power.quality import conditional_power_quality
from pipeline_common import DEFAULT_OUTPUT_ROOT, DEFAULT_RAW_ROOT, find_hop_voltage, find_powerwatch, read_config


def legacy_quality(frame: pd.DataFrame) -> dict:
    # The inherited notebook used a joint voltage/frequency filter for BOTH outcomes.
    keep = frame.voltage.between(23, 400) & frame.frequency.between(30, 70)
    data = frame[keep]
    result = {"legacy_joint_valid_n": len(data),
              "legacy_joint_voltage_quality_pct": data.voltage.between(207, 253).mean() * 100}
    for label, delta in [("1", .5), ("5", 2.5), ("10", 5)]:
        result[f"legacy_joint_frequency_{label}_pct"] = data.frequency.between(50-delta, 50+delta).mean() * 100
    return result


def legacy_uptime(frame: pd.DataFrame, minutes: int) -> dict:
    data = frame.dropna(subset=["voltage"])
    if data.empty:
        return {"legacy_row_count_uptime_pct": float("nan")}
    expected = int((data.time.max() - data.time.min()).total_seconds() / (60 * minutes)) + 1
    return {"legacy_row_count_uptime_pct": (data.voltage > 23).sum() / expected * 100,
            "legacy_expected_intervals": expected}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw-root", type=Path, default=DEFAULT_RAW_ROOT)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    args = parser.parse_args()
    output = args.output_root / "baseline_audit"
    output.mkdir(parents=True, exist_ok=True)
    canonical = {r["sensor_id"]: r["preferred_version"] for r in read_config("canonical_powerwatch.csv")}
    cache, inventory, daily = {}, [], []

    def load(sensor: str, platform: str) -> pd.DataFrame:
        if sensor in cache:
            return cache[sensor]
        path = (find_hop_voltage(args.raw_root, sensor) if platform == "HOP" else
                find_powerwatch(args.raw_root, sensor, canonical.get(sensor, "original")))
        data = read_hop_voltage(path) if platform == "HOP" else read_powerwatch(path)
        valid = data.dropna(subset=["voltage"])
        inv = {"sensor_id": sensor, "platform": platform,
               "file": str(path.relative_to(args.raw_root)),
               "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
               "rows": len(data), "valid_voltage_rows": len(valid),
               "duplicate_timestamp_rows": int(data.time.duplicated().sum()),
               "first_valid": valid.time.min(), "last_valid": valid.time.max(),
               "low_voltage_rows": int((valid.voltage <= 23).sum())}
        inventory.append(inv)
        # Distinct two-minute bins prevent repeated timestamps inflating coverage.
        binned = data.set_index("time").voltage.resample("2min").median()
        day = pd.DataFrame({"observed": binned.notna(), "powered": binned > 23})
        counts = day.resample("D").sum().reset_index()
        counts["sensor_id"] = sensor
        counts["coverage_pct_of_calendar_day"] = counts.observed / 720 * 100
        daily.append(counts)
        cache[sensor] = data
        print(f"loaded {sensor}: {len(valid):,} valid voltage rows", flush=True)
        return data

    rows = []
    for window in read_config("baseline_audit_windows.csv"):
        frame = load(window["sensor_id"], window["platform"])
        start, end = [pd.Timestamp(window[k], tz="UTC") for k in ("start_inclusive", "end_exclusive")]
        selected = frame[(frame.time >= start) & (frame.time < end)]
        valid = selected.dropna(subset=["voltage"])
        row = {**window, "valid_voltage_rows": len(valid),
               "first_valid": valid.time.min(), "last_valid": valid.time.max(),
               **monitoring_summary({window["sensor_id"]: selected}),
               **legacy_uptime(selected, 1 if window["platform"] == "HOP" else 2),
               **conditional_power_quality(selected)}
        # Also expose the FULL requested calendar window, including empty edges.
        full = monitoring_summary({window["sensor_id"]: selected}, start=start, end=end)
        row.update({f"calendar_{k}": v for k, v in full.items()
                    if k in ("expected_intervals", "coverage_pct", "expected_window_uptime_pct")})
        if window["platform"] == "PowerWatch":
            row.update(legacy_quality(selected))
        rows.append(row)
    pd.DataFrame(rows).to_csv(output / "single_sensor_comparisons.csv", index=False)

    post = []
    periods = read_config("analysis_periods.csv")
    for pair in read_config("paired_sensors.csv"):
        fac = pair["facility_code"]
        start = pd.Timestamp(next(r["start_date"] for r in periods
                                  if r["facility_code"] == fac and r["period_type"] == "powerwatch_post_source_start"), tz="UTC")
        exclusions = [(pd.Timestamp(r["start_date"], tz="UTC"),
                       pd.Timestamp(r["end_date"], tz="UTC") + pd.Timedelta(days=1) if r["end_date"] else None)
                      for r in periods if r["facility_code"] == fac and r["period_type"] == "telemetry_exclusion"]
        frames = {pair["hop_sensor"]: load(pair["hop_sensor"], "HOP"),
                  pair["powerwatch_sensor"]: load(pair["powerwatch_sensor"], "PowerWatch")}
        frames = {k: d[d.time >= start] for k, d in frames.items()}
        # Remove excluded readings BEFORE determining shared valid endpoints.
        for a, b in exclusions:
            frames = {k: d[~((d.time >= a) & ((d.time < b) if b is not None else True))]
                      for k, d in frames.items()}
        paired = monitoring_summary(frames, exclusions=exclusions)
        post.append({**pair, "sensor_basis": "paired_co_source", **paired})
        for sensor, frame in frames.items():
            post.append({**pair, "sensor_basis": f"single_{sensor}_same_paired_window",
                         **monitoring_summary({sensor: frame},
                           start=pd.Timestamp(paired["window_start"]),
                           end=pd.Timestamp(paired["window_end_inclusive"]) + pd.Timedelta(minutes=2),
                           exclusions=exclusions)})
    pd.DataFrame(post).to_csv(output / "post_sensor_comparison.csv", index=False)
    pd.DataFrame(inventory).to_csv(output / "input_inventory.csv", index=False)
    pd.concat(daily, ignore_index=True).to_csv(output / "daily_sensor_coverage.csv", index=False)
    print(pd.DataFrame(rows)[["window_id", "observed_uptime_pct", "expected_window_uptime_pct",
                             "voltage_quality_pct"]].round(3).to_string(index=False))
    print(f"Audit outputs: {output}")


if __name__ == "__main__":
    main()
