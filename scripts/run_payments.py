#!/usr/bin/env python3
"""Generate payment, OPEX, CAPEX, and working-fund manuscript outputs."""

from __future__ import annotations

import argparse
import html
from pathlib import Path

import pandas as pd

from drc_power.payments import (
    FACILITY_CODES,
    SUBSEQUENT_CAPEX_CATEGORIES,
    facility_payment_summary,
    monthly_cash_flow,
    outflows_by_facility_category,
    overall_payment_summary,
    read_payment_ledger,
)
from pipeline_common import DEFAULT_OUTPUT_ROOT, PROJECT_ROOT

FACILITY_COLORS = {
    "CH1": "#756bb1", "CSR1": "#ef6f9e", "CSR2": "#2b8cbe",
    "CSR3": "#35a98b", "CSR4": "#f28e2b", "HGR1": "#edc948",
}


def text(parts: list[str], x: float, y: float, value: str, size: int = 12, **attrs: str) -> None:
    options = " ".join(f'{key.replace("_", "-")}="{html.escape(str(val))}"' for key, val in attrs.items())
    parts.append(f'<text x="{x}" y="{y}" font-family="sans-serif" font-size="{size}" {options}>{html.escape(value)}</text>')


def draw_initial_capex(parts: list[str], components: pd.DataFrame) -> None:
    left, top, plot_w, plot_h = 120, 85, 1180, 220
    text(parts, 70, 62, "Panel A — USAID-funded initial standardized deployment CAPEX", 18, font_weight="bold")
    colors = {
        "OGB FLEX": "#17365d", "CHIARA water system": "#2b8cbe", "Embrace infant warmer": "#76b7b2",
        "Sterilizer": "#59a14f", "Oxygen concentrator": "#edc948", "Ocean freight": "#9c755f",
        "Import agent and documentation": "#bab0ab", "Import duties": "#f28e2b",
        "CIF port and other duties": "#b07aa1", "VAT": "#e15759",
        "In-country delivery and installation": "#4e79a7",
    }
    maximum = 8000.0
    bar_w = 300
    for index, group in enumerate(("equipment", "implementation")):
        group_data = components[components["cost_group"] == group]
        x = left + 250 + index * 520; base = top + plot_h
        for _, row in group_data.iterrows():
            height = plot_h * float(row["amount_usd"]) / maximum
            parts.append(f'<rect x="{x}" y="{base-height}" width="{bar_w}" height="{height}" fill="{colors[row["component"]]}"/>')
            base -= height
        total = group_data["amount_usd"].sum()
        text(parts, x + bar_w / 2, base - 9, f"${total:,.0f}", 14, text_anchor="middle", font_weight="bold")
        text(parts, x + bar_w / 2, top + plot_h + 24, group.title(), 14, text_anchor="middle")
    installed = components["amount_usd"].sum()
    text(parts, 70, 350, f"Standard installed package: ${installed:,.0f}", 15, font_weight="bold")
    text(parts, 420, 350, "Budget reference; initial systems funded by USAID, not by facility payment revenue.", 13, fill="#555")
    legend_y = 370
    for i, component in enumerate(components["component"]):
        col, row = i % 4, i // 4; x = 75 + col * 340; y = legend_y + row * 18
        parts += [f'<rect x="{x}" y="{y}" width="11" height="11" fill="{colors[component]}"/>']
        text(parts, x + 17, y + 10, component, 10)


def prepare_opex(outflows: pd.DataFrame) -> pd.DataFrame:
    opex_columns = [column for column in outflows.columns if column not in SUBSEQUENT_CAPEX_CATEGORIES]
    frame = outflows[opex_columns].copy()
    frame["Administrative/central OPEX"] = 0.0
    if "ADMIN" in frame.index:
        admin_total = frame.loc["ADMIN", opex_columns].sum()
        frame.loc["ADMIN", opex_columns] = 0.0
        frame.loc["ADMIN", "Administrative/central OPEX"] = admin_total
    frame = frame.rename(columns={"Installation & deployment": "Deployment/reinstallation"})
    return frame


def draw_opex(parts: list[str], opex: pd.DataFrame) -> None:
    left, top, plot_w, plot_h = 95, 505, 1260, 240
    text(parts, 70, 475, "Panel B — Ledger-recorded OPEX by facility and pooled administration", 18, font_weight="bold")
    categories = list(opex.columns); facilities = list(opex.index)
    palette = ["#e15759", "#f28e2b", "#76b7b2", "#59a14f", "#edc948", "#b07aa1", "#9c755f", "#777777"]
    colors = {category: palette[i % len(palette)] for i, category in enumerate(categories)}
    maximum = max(float(opex.sum(axis=1).max()), 1) * 1.10; cell = plot_w / len(facilities); bar_w = cell * 0.58
    for tick in range(4):
        value = maximum * tick / 3; y = top + plot_h * (1 - tick / 3)
        parts += [f'<line x1="{left}" y1="{y}" x2="{left+plot_w}" y2="{y}" stroke="#ececec"/>']
        text(parts, left - 8, y + 4, f"${value:,.0f}", 10, text_anchor="end")
    for i, facility in enumerate(facilities):
        x = left + (i + 0.5) * cell - bar_w / 2; base = top + plot_h
        for category in categories:
            value = float(opex.loc[facility, category]); height = plot_h * value / maximum
            if height:
                parts.append(f'<rect x="{x}" y="{base-height}" width="{bar_w}" height="{height}" fill="{colors[category]}"/>')
                base -= height
        text(parts, x + bar_w / 2, top + plot_h + 20, str(facility), 12, text_anchor="middle")
    legend_y = top + plot_h + 42
    for i, category in enumerate(categories):
        col, row = i % 4, i // 4; x = 75 + col * 340; y = legend_y + row * 18
        parts.append(f'<rect x="{x}" y="{y}" width="11" height="11" fill="{colors[category]}"/>')
        text(parts, x + 17, y + 10, category, 10)


def draw_revenue(parts: list[str], facility: pd.DataFrame) -> None:
    left, top, plot_w, plot_h = 95, 875, 1260, 235
    text(parts, 70, 845, "Panel C — Facility payment revenue and timing", 18, font_weight="bold")
    maximum = max(float(facility["received_usd"].max()), 1) * 1.12; cell = plot_w / len(facility); bar_w = cell * 0.52
    for tick in range(4):
        value = maximum * tick / 3; y = top + plot_h * (1 - tick / 3)
        parts += [f'<line x1="{left}" y1="{y}" x2="{left+plot_w}" y2="{y}" stroke="#ececec"/>']
        text(parts, left - 8, y + 4, f"${value:,.0f}", 10, text_anchor="end")
        text(parts, left + plot_w + 8, y + 4, f"{100*tick/3:.0f}%", 10)
    for i, row in facility.reset_index(drop=True).iterrows():
        code = row["facility_code"]; x = left + (i + 0.5) * cell; height = plot_h * float(row["received_usd"]) / maximum
        parts.append(f'<rect x="{x-bar_w/2}" y="{top+plot_h-height}" width="{bar_w}" height="{height}" fill="{FACILITY_COLORS[code]}"/>')
        y_point = top + plot_h * (1 - float(row["on_time_pct"]) / 100)
        parts += [f'<circle cx="{x}" cy="{y_point}" r="6" fill="#111"/>']
        text(parts, x, y_point - 10, f'{row["on_time_pct"]:.1f}%', 10, text_anchor="middle")
        text(parts, x, top + plot_h + 20, code, 12, text_anchor="middle")
        text(parts, x, top + plot_h - height - 8, f'${row["received_usd"]:,.0f}', 10, text_anchor="middle")
    text(parts, 70, 1145, "Bars: revenue received (left axis). Black points: share of remittances recorded on time (right axis).", 11, fill="#555")


def draw_working_fund(parts: list[str], overall: pd.Series) -> None:
    left, top, plot_w, plot_h = 130, 1225, 1170, 230
    text(parts, 70, 1195, "Panel D — Working-fund bridge and subsequent capital deployment", 18, font_weight="bold")
    revenue = float(overall["payment_revenue_usd"]); opex = float(overall["opex_total_usd"])
    capex = float(overall["additional_system_capex_usd"]); pre_capex = revenue - opex; ending = pre_capex - capex
    maximum = revenue * 1.08; bar_w = 150; xs = [left + 70, left + 330, left + 590, left + 850, left + 1110]
    entries = [
        ("Revenue", revenue, 0, "#59a14f", revenue),
        ("OPEX", opex, pre_capex, "#8c8c8c", -opex),
        ("Working fund\nbefore expansion", pre_capex, 0, "#35a98b", pre_capex),
        ("Subsequent CAPEX", capex, ending, "#17365d", -capex),
        ("Ending ledger\nbalance", ending, 0, "#2b8cbe", ending),
    ]
    for i, (label, height_value, base_value, color, signed) in enumerate(entries):
        x = xs[i] - bar_w / 2; y_base = top + plot_h * (1 - base_value / maximum); height = plot_h * height_value / maximum
        parts.append(f'<rect x="{x}" y="{y_base-height}" width="{bar_w}" height="{height}" fill="{color}"/>')
        text(parts, xs[i], y_base - height - 9, f'{"−" if signed < 0 else ""}${abs(signed):,.0f}', 12, text_anchor="middle", font_weight="bold")
        for line_no, line in enumerate(label.split("\n")):
            text(parts, xs[i], top + plot_h + 20 + 15 * line_no, line, 11, text_anchor="middle")
        if i < len(entries) - 1:
            next_level = (revenue, pre_capex, pre_capex, ending)[i]
            y = top + plot_h * (1 - next_level / maximum)
            parts.append(f'<line x1="{xs[i]+bar_w/2}" y1="{y}" x2="{xs[i+1]-bar_w/2}" y2="{y}" stroke="#777" stroke-dasharray="4,3"/>')
    text(parts, 70, 1515, "The later additional system was funded from accumulated facility-payment revenue after recorded OPEX.", 12, fill="#555")


def write_figure(path: Path, components: pd.DataFrame, opex: pd.DataFrame,
                 facility: pd.DataFrame, overall: pd.Series) -> None:
    width, height = 1450, 1540
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
             '<rect width="100%" height="100%" fill="white"/>']
    text(parts, width / 2, 31, "Capital structure, operating cash flow, and facility payments", 23,
         text_anchor="middle", font_weight="bold")
    draw_initial_capex(parts, components)
    draw_opex(parts, opex)
    draw_revenue(parts, facility)
    draw_working_fund(parts, overall)
    parts.append("</svg>")
    path.write_text("\n".join(parts), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ledger", type=Path, default=PROJECT_ROOT / "data" / "public" / "payments" / "payment_ledger_anonymized.csv")
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    args = parser.parse_args()
    output = args.output_root / "payments"; output.mkdir(parents=True, exist_ok=True)
    data = read_payment_ledger(args.ledger)
    components = pd.read_csv(PROJECT_ROOT / "config" / "capex_components.csv")
    facility = facility_payment_summary(data); facility.to_csv(output / "facility_payment_summary.csv", index=False)
    overall = overall_payment_summary(data); overall.to_csv(output / "overall_payment_summary.csv", index=False)
    monthly = monthly_cash_flow(data); monthly.to_csv(output / "monthly_cash_flow.csv")
    outflows = outflows_by_facility_category(data); outflows.to_csv(output / "outflows_by_facility_and_category.csv")
    opex = prepare_opex(outflows); opex.to_csv(output / "opex_by_facility_and_category.csv")
    subsequent_capex = outflows[[column for column in outflows.columns if column in SUBSEQUENT_CAPEX_CATEGORIES]]
    subsequent_capex.to_csv(output / "subsequent_capex_by_facility.csv")
    write_figure(output / "figure6_financial_sustainability.svg", components, opex, facility, overall.iloc[0])
    print(f"payments: {len(data)} ledger rows, ${overall.loc[0, 'payment_revenue_usd']:,.0f} received")


if __name__ == "__main__":
    main()
