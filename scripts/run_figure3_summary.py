#!/usr/bin/env python3
"""Generate Figure 3 source comparisons and a denominator sensitivity figure."""

from __future__ import annotations
import argparse
from pathlib import Path
import pandas as pd
from drc_power.figure3 import reconstructed_comparisons
from pipeline_common import DEFAULT_OUTPUT_ROOT, read_config, write_pre_post_triptych_svg


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument("--pqr-policy", choices=["joint", "independent"], default="joint",
                        help="Joint validity reproduces inherited PQR; independent is the sensitivity.")
    args = parser.parse_args()
    reliability = pd.read_csv(args.output_root / "reliability" / "manuscript_uptime_sensitivity.csv")
    quality = pd.read_csv(args.output_root / "power_quality" / "post_flex_conditional_quality_by_facility.csv")
    primary = pd.DataFrame([r for r in read_config("paired_sensors.csv") if r["primary_facility_result"].lower() == "true"])
    reliability = reliability.merge(primary[["facility_code", "shared_source"]], on=["facility_code", "shared_source"])
    pre = pd.DataFrame(read_config("manuscript_pre_results.csv"))
    for column in ("uptime_pct", "voltage_quality_pct", "frequency_quality_5_pct"):
        pre[column] = pd.to_numeric(pre[column])
    audit = pd.read_csv(args.output_root / "baseline_audit" / "single_sensor_comparisons.csv")
    pre = reconstructed_comparisons(pre, audit, args.pqr_policy)
    quality_suffix = "joint_pooled" if args.pqr_policy == "joint" else "pooled"
    quality = quality.rename(columns={
        f"voltage_quality_pct_{quality_suffix}": "figure_voltage_pct",
        f"frequency_quality_5_pct_{quality_suffix}": "figure_frequency_5_pct",
    })
    summary = pre.merge(
        reliability[["facility_code", "manuscript_uptime_expected_window_pct"]], on="facility_code"
    ).merge(
        quality[["facility_code", "figure_voltage_pct", "figure_frequency_5_pct"]],
        on="facility_code",
    ).rename(columns={
        "uptime_pct": "uptime_pre_pct",
        "manuscript_uptime_expected_window_pct": "uptime_post_pct",
        "voltage_quality_pct": "voltage_pre_pct",
        "figure_voltage_pct": "voltage_post_pct",
        "frequency_quality_5_pct": "frequency_5_pre_pct",
        "figure_frequency_5_pct": "frequency_5_post_pct",
        "status": "pre_status",
    })
    order = {code: i for i, code in enumerate(["HGR1", "CH1", "CSR1", "CSR2", "CSR3", "CSR4"])}
    summary["sort"] = summary["facility_code"].map(order)
    summary = summary.sort_values("sort").drop(columns="sort")
    summary["post_uptime_sensor_basis"] = "paired_hop_powerwatch_any_sensor_powered"
    summary["post_pqr_sensor_basis"] = "powerwatch_source_sensors_pooled"
    output = args.output_root / "figure3"; output.mkdir(parents=True, exist_ok=True)
    stem = "pre_post_summary" if args.pqr_policy == "joint" else "source_comparison_independent_pqr"
    summary.to_csv(output / f"{stem}.csv", index=False)
    write_pre_post_triptych_svg(output / f"{stem}.svg", summary.to_dict("records"),
                               source_comparison=True)
    # ±1% and ±10% are computed only for the three reconstructed comparisons;
    # inherited ±5% numbers must never be relabelled as another tolerance.
    thresholds = []
    for row in summary.to_dict("records"):
        for tolerance in ("1", "5", "10"):
            post = quality[quality.facility_code == row["facility_code"]].iloc[0]
            thresholds.append({"facility_code": row["facility_code"], "frequency_tolerance_pct": int(tolerance),
                               "existing_source_frequency_pct": row.get(f"frequency_quality_{tolerance}_pct", float("nan"))
                                   if tolerance != "5" else row["frequency_5_pre_pct"],
                               "protected_circuit_frequency_pct": post[
                                   "figure_frequency_5_pct" if tolerance == "5" else
                                   f"frequency_quality_{tolerance}_pct_{quality_suffix}"],
                               "baseline_status": row["pre_status"], "pqr_denominator_policy": args.pqr_policy})
    pd.DataFrame(thresholds).to_csv(output / f"frequency_thresholds_{args.pqr_policy}.csv", index=False)
    print(f"figure 3 summary: {len(summary)} facilities")


if __name__ == "__main__":
    main()
