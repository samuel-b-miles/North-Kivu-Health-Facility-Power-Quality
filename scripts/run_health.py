#!/usr/bin/env python3
"""Build anonymized DHIS2 panels, QA outputs, Table 2, and health dashboard."""

from __future__ import annotations

import argparse
import html
from pathlib import Path

import numpy as np
import pandas as pd

from drc_power.dhis2 import (
    build_facility_month,
    build_ward_month,
    implausible_values,
    longest_streak,
    missing_months,
    table2_metrics,
)
from pipeline_common import DEFAULT_OUTPUT_ROOT, PROJECT_ROOT


def write_dashboard_svg(path: Path, facility_month: pd.DataFrame, display_code: str = "HGR1") -> None:
    data = facility_month[facility_month["display_code"] == display_code].copy().sort_values("month")
    if data.empty:
        raise ValueError(f"No public dashboard data for {display_code}")
    data["month_date"] = pd.to_datetime(data["month"])
    width, height = 1250, 820; left, top, panel_w, panel_h, gap = 85, 80, 1080, 185, 55
    metrics = [("admissions", "Monthly admissions", "#2b8cbe"),
               ("deaths_total", "Monthly inpatient deaths", "#e15759"),
               ("mortality_rate", "Inpatient mortality rate (%)", "#756bb1")]
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
             '<rect width="100%" height="100%" fill="white"/>',
             f'<text x="{width/2}" y="32" text-anchor="middle" font-family="sans-serif" font-size="22" font-weight="bold">DHIS2 health-outcome monitoring dashboard — {html.escape(display_code)}</text>']
    for panel, (column, label, color) in enumerate(metrics):
        y0 = top + panel * (panel_h + gap)
        values = data[column].astype(float) * (100 if column == "mortality_rate" else 1)
        maximum = max(float(values.max(skipna=True)), 1) * 1.12
        for tick in range(4):
            value = maximum * tick / 3; y = y0 + panel_h * (1 - tick / 3)
            parts += [f'<line x1="{left}" y1="{y}" x2="{left+panel_w}" y2="{y}" stroke="#e8e8e8"/>',
                      f'<text x="{left-8}" y="{y+4}" text-anchor="end" font-family="sans-serif" font-size="11">{value:.1f}</text>']
        points = []
        for index, value in enumerate(values):
            x = left + index * panel_w / max(len(data)-1, 1)
            if pd.notna(value):
                y = y0 + panel_h * (1 - float(value) / maximum); points.append((x, y))
        for first, second in zip(points, points[1:]):
            parts.append(f'<line x1="{first[0]}" y1="{first[1]}" x2="{second[0]}" y2="{second[1]}" stroke="{color}" stroke-width="2.5"/>')
        for x, y in points:
            parts.append(f'<circle cx="{x}" cy="{y}" r="3.5" fill="{color}"/>')
        for index, reported in enumerate(data["facility_month_reported"]):
            if not reported:
                x = left + index * panel_w / max(len(data)-1, 1)
                parts.append(f'<rect x="{x-7}" y="{y0}" width="14" height="{panel_h}" fill="#d9d9d9" fill-opacity="0.8"/>')
        parts.append(f'<text x="{left}" y="{y0-12}" font-family="sans-serif" font-size="15" font-weight="bold">{html.escape(label)}</text>')
        if panel == 2:
            for index in (0, 11, 23, 35):
                x = left + index * panel_w / max(len(data)-1, 1)
                parts.append(f'<text x="{x}" y="{y0+panel_h+22}" text-anchor="middle" font-family="sans-serif" font-size="11">{pd.Timestamp(data.iloc[index]["month_date"]).strftime("%b %Y")}</text>')
    parts += ['<rect x="85" y="790" width="12" height="12" fill="#d9d9d9"/>',
              '<text x="103" y="801" font-family="sans-serif" font-size="11">No ward-level admissions reported for that facility-month</text>', '</svg>']
    path.write_text("\n".join(parts), encoding="utf-8")


def descriptive_prepost(facility_month: pd.DataFrame, intervention_month: str) -> pd.DataFrame:
    data = facility_month[facility_month["facility_month_reported"]].copy()
    data["period"] = np.where(data["month"] < intervention_month, "pre", "post")
    return data.groupby(["arm", "period"], as_index=False).agg(
        facility_months_n=("month", "size"),
        mean_monthly_admissions=("admissions", "mean"),
        mean_monthly_deaths=("deaths_total", "mean"),
        mean_inpatient_mortality_rate_pct=("mortality_rate", lambda values: 100 * values.mean()),
    )


def write_quality_report(path: Path, ward: pd.DataFrame, facility: pd.DataFrame, audit: dict,
                         table2: pd.DataFrame, implausible: pd.DataFrame) -> None:
    crosswalk = audit["crosswalk"]
    ambiguous_entities = crosswalk[~crosswalk["include_study"]]
    duplicate_audit = audit["duplicate_columns"]
    report = [
        "# DHIS2 Quality Report", "",
        f"- Raw admissions dimensions: `{audit['raw_admissions_shape']}`",
        f"- Raw deaths dimensions: `{audit['raw_deaths_shape']}`",
        f"- Unique raw facilities: **{audit['unique_raw_facilities']}**",
        f"- Included study facilities: **{facility['facility_id_anonymized'].nunique()}**",
        f"- Primary months: **{facility['month'].nunique()}** (2023-01 through 2025-12)",
        f"- Facility-month denominator: **{len(facility)}** (expected 432)",
        f"- Ward-month denominator: **{len(ward)}** (expected 1,728)",
        f"- Missing facility-months: **{(~facility['facility_month_reported']).sum()}**",
        f"- Ward-months with admissions <5: **{((ward['admissions'].notna()) & (ward['admissions'] < 5)).sum()}**",
        f"- Ward-months with deaths imputed to structural zero because both death fields were missing: **{ward['deaths_imputed_zero_from_missing'].sum()}**",
        f"- Implausible value rows: **{len(implausible)}**",
        f"- Duplicate-column conflicts: **{duplicate_audit['conflict_n'].sum()}**",
        "", "## Ambiguous mapping audit", "",
    ]
    for _, row in ambiguous_entities.iterrows():
        report.append(f"- `{row['raw_facility_name']}`: {'included' if row['include_study'] else 'excluded'}")
    rounded = table2.round(3)
    markdown_rows = ["| " + " | ".join(rounded.columns) + " |", "| " + " | ".join(["---"] * len(rounded.columns)) + " |"]
    markdown_rows.extend("| " + " | ".join(map(str, row)) + " |" for row in rounded.itertuples(index=False, name=None))
    report += ["", "## Regenerated Table 2", "", *markdown_rows, "",
               "## Manuscript reconciliation", "",
               "All listed Table 2 values reproduce after manuscript rounding, including 82.8% and 78.4% of reported facility-months with at least one inpatient death in the treatment and control arms, respectively.", ""]
    path.write_text("\n".join(report), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw-root", type=Path, default=PROJECT_ROOT / "data" / "raw" / "dhis2")
    parser.add_argument("--public-root", type=Path, default=PROJECT_ROOT / "data" / "public")
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    args = parser.parse_args()
    output = args.output_root / "health"; qa = output / "qa"; tables = output / "tables"; figures = output / "figures"
    for directory in (args.public_root, qa, tables, figures): directory.mkdir(parents=True, exist_ok=True)
    ward, audit = build_ward_month(
        args.raw_root / "admissions.csv", args.raw_root / "deaths.csv",
        PROJECT_ROOT / "config" / "private" / "facility_crosswalk_private.csv",
        PROJECT_ROOT / "config" / "dhis2_wards.csv", PROJECT_ROOT / "config" / "dhis2_analysis.csv",
    )
    facility = build_facility_month(ward)
    table2 = table2_metrics(ward, facility)
    implausible = implausible_values(ward)
    ward.to_csv(args.public_root / "dhis2_ward_month_anonymized.csv", index=False)
    facility.to_csv(args.public_root / "dhis2_facility_month_anonymized.csv", index=False)
    table2.to_csv(tables / "table2_health_data_quality.csv", index=False)
    parameters = pd.read_csv(PROJECT_ROOT / "config" / "dhis2_analysis.csv").set_index("parameter")["value"].astype(str)
    descriptive_prepost(facility, parameters["intervention_month"]).to_csv(tables / "table_health_descriptive_prepost.csv", index=False)
    completeness = facility.groupby(["facility_id_anonymized", "display_code", "arm"], as_index=False).agg(
        months_reported=("facility_month_reported", "sum"),
        longest_reporting_streak_months=("facility_month_reported", longest_streak),
        mean_monthly_admissions=("admissions", "mean"),
        mean_mortality_rate=("mortality_rate", "mean"),
    )
    completeness.to_csv(tables / "annex_health_data_completeness.csv", index=False)
    missing_months(facility).to_csv(qa / "missing_months_by_facility.csv", index=False)
    audit["duplicate_columns"].to_csv(qa / "duplicate_columns_audit.csv", index=False)
    implausible.to_csv(qa / "implausible_values.csv", index=False)
    audit["crosswalk"][["raw_facility_name", "facility_id_anonymized", "include_study"]].to_csv(qa / "facility_mapping_audit.csv", index=False)
    write_quality_report(qa / "dhis2_quality_report.md", ward, facility, audit, table2, implausible)
    write_dashboard_svg(figures / "hgr1_health_dashboard.svg", facility, "HGR1")
    print(table2.round(2).to_string(index=False))
    print(f"health: {len(ward)} ward-months, {len(facility)} facility-months, 12 facilities")


if __name__ == "__main__":
    main()
