#!/usr/bin/env python3
"""Generate audited payment/cost tables and the provisional Figure 6."""

from __future__ import annotations

import argparse
import html
from pathlib import Path

import pandas as pd

from drc_power.payments import (
    CAPEX_CATEGORIES,
    FACILITY_CODES,
    facility_payment_summary,
    monthly_cash_flow,
    outflows_by_facility_category,
    overall_payment_summary,
    read_payment_ledger,
)
from pipeline_common import DEFAULT_OUTPUT_ROOT, PROJECT_ROOT


def write_cost_panel(parts: list[str], frame: pd.DataFrame, title: str, top: int, height: int,
                     category_colors: dict[str, str]) -> None:
    left, plot_w = 95, 1260
    facilities = list(frame.index); categories = list(frame.columns)
    maximum = max(float(frame.sum(axis=1).max()), 1) * 1.10
    cell = plot_w / len(facilities); bar_w = cell * 0.58
    parts.append(f'<text x="{left}" y="{top-18}" font-family="sans-serif" font-size="17" font-weight="bold">{html.escape(title)}</text>')
    for tick in range(4):
        value = maximum * tick / 3; y = top + height * (1 - tick / 3)
        parts += [f'<line x1="{left}" y1="{y}" x2="{left+plot_w}" y2="{y}" stroke="#ececec"/>',
                  f'<text x="{left-8}" y="{y+4}" text-anchor="end" font-family="sans-serif" font-size="10">${value:,.0f}</text>']
    for i, facility in enumerate(facilities):
        x = left + (i + 0.5) * cell - bar_w / 2; base = top + height
        for category in categories:
            value = float(frame.loc[facility, category]); bar_height = height * value / maximum
            if bar_height:
                parts.append(f'<rect x="{x:.2f}" y="{base-bar_height:.2f}" width="{bar_w:.2f}" height="{bar_height:.2f}" fill="{category_colors[category]}"/>')
                base -= bar_height
        parts.append(f'<text x="{x+bar_w/2}" y="{top+height+19}" text-anchor="middle" font-family="sans-serif" font-size="12">{html.escape(str(facility))}</text>')
    legend_y = top + height + 43
    for k, category in enumerate(categories):
        x = left + (k % 4) * 315; y = legend_y + (k // 4) * 19
        parts += [f'<rect x="{x}" y="{y}" width="12" height="12" fill="{category_colors[category]}"/>',
                  f'<text x="{x+18}" y="{y+11}" font-family="sans-serif" font-size="11">{html.escape(str(category))}</text>']


def write_figure(path: Path, monthly: pd.DataFrame, capex: pd.DataFrame, opex: pd.DataFrame) -> None:
    width, height = 1450, 1250
    # Match the established manuscript palette using public facility codes.
    colors = {"CH1": "#756bb1", "CSR1": "#ef6f9e", "CSR2": "#2b8cbe", "CSR3": "#35a98b", "CSR4": "#f28e2b", "HGR1": "#edc948"}
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
             '<rect width="100%" height="100%" fill="white"/>',
             '<text x="725" y="30" text-anchor="middle" font-family="sans-serif" font-size="23" font-weight="bold">Facility payments and recorded expenditures</text>']

    # Panel A: monthly facility payments, recorded outflows, and cumulative balance.
    left, top, plot_w, plot_h = 95, 80, 1260, 350
    monthly_max = max(float(monthly["facility_payments_usd"].max()), float(monthly["recorded_outflows_usd"].max()), 1) * 1.12
    cumulative_max = max(float(monthly["cumulative_ledger_balance_usd"].max()), 1) * 1.12
    cell_w = plot_w / len(monthly); bar_w = cell_w * 0.72
    parts.append(f'<text x="{left}" y="{top-20}" font-family="sans-serif" font-size="17" font-weight="bold">Panel A — Monthly cash flows and cumulative ledger balance</text>')
    for tick in range(5):
        value = monthly_max * tick / 4; y = top + plot_h * (1 - tick / 4)
        parts += [f'<line x1="{left}" y1="{y}" x2="{left+plot_w}" y2="{y}" stroke="#e5e5e5"/>',
                  f'<text x="{left-8}" y="{y+4}" text-anchor="end" font-family="sans-serif" font-size="11">${value:,.0f}</text>']
        cumulative_value = cumulative_max * tick / 4
        parts.append(f'<text x="{left+plot_w+8}" y="{y+4}" font-family="sans-serif" font-size="11">${cumulative_value:,.0f}</text>')
    for j, (_, row) in enumerate(monthly.iterrows()):
        x = left + (j + 0.5) * cell_w - bar_w / 2; base = top + plot_h
        for code in FACILITY_CODES:
            value = float(row[code]); bar_h = plot_h * value / monthly_max
            parts.append(f'<rect x="{x:.2f}" y="{base-bar_h:.2f}" width="{bar_w:.2f}" height="{bar_h:.2f}" fill="{colors[code]}"/>')
            base -= bar_h
        opex_h = plot_h * float(row["opex_outflows_usd"]) / monthly_max
        capex_h = plot_h * float(row["capex_outflows_usd"]) / monthly_max
        outflow_x = x + bar_w * 0.70; outflow_w = bar_w * 0.30; outflow_base = top + plot_h
        if opex_h:
            parts.append(f'<rect x="{outflow_x:.2f}" y="{outflow_base-opex_h:.2f}" width="{outflow_w:.2f}" height="{opex_h:.2f}" fill="#8c8c8c"/>')
            outflow_base -= opex_h
        if capex_h:
            parts.append(f'<rect x="{outflow_x:.2f}" y="{outflow_base-capex_h:.2f}" width="{outflow_w:.2f}" height="{capex_h:.2f}" fill="#17365d"/>')
    points = []
    for j, value in enumerate(monthly["cumulative_ledger_balance_usd"]):
        x = left + (j + 0.5) * cell_w; y = top + plot_h * (1 - float(value) / cumulative_max)
        points.append(f"{x:.2f},{y:.2f}")
    parts.append(f'<polyline points="{" ".join(points)}" fill="none" stroke="#111" stroke-width="3" stroke-dasharray="8,5"/>')
    for j in sorted(set([0, len(monthly)//2, len(monthly)-1])):
        x = left + (j + 0.5) * cell_w; label = pd.Timestamp(monthly.index[j]).strftime("%b %Y")
        parts.append(f'<text x="{x}" y="{top+plot_h+22}" text-anchor="middle" font-family="sans-serif" font-size="11">{label}</text>')
    parts.append(f'<text transform="translate(22 {top+plot_h/2}) rotate(-90)" text-anchor="middle" font-family="sans-serif" font-size="13">Monthly cash flow (USD)</text>')
    parts.append(f'<text transform="translate({width-22} {top+plot_h/2}) rotate(90)" text-anchor="middle" font-family="sans-serif" font-size="13">Cumulative ledger balance (USD)</text>')
    legend_y = top + plot_h + 52
    for i, code in enumerate(FACILITY_CODES):
        x = left + i * 125; parts += [f'<rect x="{x}" y="{legend_y}" width="14" height="14" fill="{colors[code]}"/>', f'<text x="{x+20}" y="{legend_y+12}" font-family="sans-serif" font-size="12">{code}</text>']
    parts += [f'<rect x="{left+750}" y="{legend_y}" width="14" height="14" fill="#8c8c8c"/><text x="{left+770}" y="{legend_y+12}" font-family="sans-serif" font-size="12">OPEX</text>',
              f'<rect x="{left+835}" y="{legend_y}" width="14" height="14" fill="#17365d"/><text x="{left+855}" y="{legend_y+12}" font-family="sans-serif" font-size="12">CAPEX</text>',
              f'<line x1="{left+930}" y1="{legend_y+7}" x2="{left+960}" y2="{legend_y+7}" stroke="#111" stroke-width="3" stroke-dasharray="8,5"/><text x="{left+970}" y="{legend_y+12}" font-family="sans-serif" font-size="12">Cumulative balance</text>']

    capex_colors = {"Additional Requested Upgrade": "#17365d", "Installation & deployment": "#f28e2b"}
    opex_palette = ["#e15759", "#76b7b2", "#59a14f", "#edc948", "#b07aa1", "#9c755f"]
    opex_colors = {category: opex_palette[i % len(opex_palette)] for i, category in enumerate(opex.columns)}
    write_cost_panel(parts, capex, "Panel B — Recorded CAPEX by facility and type", 585, 230, capex_colors)
    write_cost_panel(parts, opex, "Panel C — Recorded OPEX by facility and type", 935, 230, opex_colors)
    parts.append('</svg>')
    path.write_text("\n".join(parts), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ledger", type=Path, default=PROJECT_ROOT / "data" / "public" / "payments" / "payment_ledger_anonymized.csv")
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    args = parser.parse_args()
    output = args.output_root / "payments"; output.mkdir(parents=True, exist_ok=True)
    data = read_payment_ledger(args.ledger)
    facility = facility_payment_summary(data); facility.to_csv(output / "facility_payment_summary.csv", index=False)
    overall = overall_payment_summary(data); overall.to_csv(output / "overall_payment_summary.csv", index=False)
    monthly = monthly_cash_flow(data); monthly.to_csv(output / "monthly_cash_flow.csv")
    outflows = outflows_by_facility_category(data); outflows.to_csv(output / "outflows_by_facility_and_category.csv")
    capex_columns = [column for column in outflows.columns if column in CAPEX_CATEGORIES]
    opex_columns = [column for column in outflows.columns if column not in CAPEX_CATEGORIES]
    capex = outflows[capex_columns]; opex = outflows[opex_columns]
    capex.to_csv(output / "capex_by_facility_and_type.csv")
    opex.to_csv(output / "opex_by_facility_and_type.csv")
    write_figure(output / "figure6_payments_and_costs.svg", monthly, capex, opex)
    print(f"payments: {len(data)} ledger rows, ${overall.loc[0, 'payment_revenue_usd']:,.0f} received")


if __name__ == "__main__":
    main()
