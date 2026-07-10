#!/usr/bin/env python3
"""Generate the provisional manuscript Figure 3 pre/post summary."""

from __future__ import annotations
import argparse
from pathlib import Path
import pandas as pd
from pipeline_common import DEFAULT_OUTPUT_ROOT, read_config, write_pre_post_triptych_svg


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    args = parser.parse_args()
    reliability = pd.read_csv(args.output_root / "reliability" / "manuscript_uptime_sensitivity.csv")
    quality = pd.read_csv(args.output_root / "power_quality" / "post_flex_conditional_quality_by_facility.csv")
    primary = pd.DataFrame([r for r in read_config("paired_sensors.csv") if r["primary_facility_result"].lower() == "true"])
    reliability = reliability.merge(primary[["facility_code", "shared_source"]], on=["facility_code", "shared_source"])
    pre = pd.DataFrame(read_config("manuscript_pre_results.csv"))
    for column in ("uptime_pct", "voltage_quality_pct", "frequency_quality_5_pct"):
        pre[column] = pd.to_numeric(pre[column])
    summary = pre.merge(
        reliability[["facility_code", "manuscript_uptime_expected_window_pct"]], on="facility_code"
    ).merge(
        quality[["facility_code", "voltage_quality_pct_pooled", "frequency_quality_5_pct_pooled"]],
        on="facility_code",
    ).rename(columns={
        "uptime_pct": "uptime_pre_pct",
        "manuscript_uptime_expected_window_pct": "uptime_post_pct",
        "voltage_quality_pct": "voltage_pre_pct",
        "voltage_quality_pct_pooled": "voltage_post_pct",
        "frequency_quality_5_pct": "frequency_5_pre_pct",
        "frequency_quality_5_pct_pooled": "frequency_5_post_pct",
        "status": "pre_status",
    })
    order = {code: i for i, code in enumerate(["HGR1", "CH1", "CSR1", "CSR2", "CSR3", "CSR4"])}
    summary["sort"] = summary["facility_code"].map(order)
    summary = summary.sort_values("sort").drop(columns="sort")
    output = args.output_root / "figure3"; output.mkdir(parents=True, exist_ok=True)
    summary.to_csv(output / "pre_post_summary.csv", index=False)
    write_pre_post_triptych_svg(output / "pre_post_summary.svg", summary.to_dict("records"))
    print(f"figure 3 summary: {len(summary)} facilities")


if __name__ == "__main__":
    main()
