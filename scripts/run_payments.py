#!/usr/bin/env python3
"""Generate CAPEX, payment-revenue, and payment-timing manuscript outputs."""

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


def standard_package_steps(components: pd.DataFrame) -> list[tuple[str, float, str]]:
    amount = components.set_index("component")["amount_usd"]
    biomedical = amount["Embrace infant warmer"] + amount["Sterilizer"] + amount["Oxygen concentrator"]
    freight_agent = amount["Ocean freight"] + amount["Import agent and documentation"]
    return [
        ("OGB FLEX", amount["OGB FLEX"], "step"),
        ("CHIARA", amount["CHIARA water system"], "step"),
        ("Biomedical\nequipment", biomedical, "step"),
        ("Equipment\nsubtotal", components.loc[components["cost_group"] == "equipment", "amount_usd"].sum(), "total"),
        ("Freight +\nagent", freight_agent, "step"),
        ("Import\nduties", amount["Import duties"], "step"),
        ("CIF/port", amount["CIF port and other duties"], "step"),
        ("VAT", amount["VAT"], "step"),
        ("Delivery +\ninstallation", amount["In-country delivery and installation"], "step"),
        ("Installed\npackage", components["amount_usd"].sum(), "total"),
    ]


def draw_package_waterfall(parts: list[str], components: pd.DataFrame) -> None:
    left, top, plot_w, plot_h = 90, 82, 1270, 245
    text(parts, 70, 60, "Panel A — Standard reference package CAPEX", 18, font_weight="bold")
    steps = standard_package_steps(components); maximum = steps[-1][1] * 1.10
    cell = plot_w / len(steps); bar_w = cell * 0.62; running = 0.0
    step_colors = ["#17365d", "#2b8cbe", "#59a14f", "#17365d", "#9c755f", "#f28e2b", "#b07aa1", "#e15759", "#4e79a7", "#35a98b"]
    prior_level = 0.0
    for index, (label, value, kind) in enumerate(steps):
        x = left + (index + 0.5) * cell - bar_w / 2
        if kind == "step":
            base = running; running += value; top_value = running
        else:
            base = 0; top_value = value
            if "Equipment" in label:
                running = value
        y_top = top + plot_h * (1 - top_value / maximum); y_base = top + plot_h * (1 - base / maximum)
        parts.append(f'<rect x="{x}" y="{y_top}" width="{bar_w}" height="{y_base-y_top}" fill="{step_colors[index]}"/>')
        text(parts, x + bar_w / 2, y_top - 7, f"${value:,.0f}", 10, text_anchor="middle", font_weight="bold")
        for line_number, line in enumerate(label.split("\n")):
            text(parts, x + bar_w / 2, top + plot_h + 18 + 13 * line_number, line, 10, text_anchor="middle")
        if index and kind == "step":
            y = top + plot_h * (1 - prior_level / maximum)
            previous_x = left + (index - 0.5) * cell + bar_w / 2
            parts.append(f'<line x1="{previous_x}" y1="{y}" x2="{x}" y2="{y}" stroke="#888" stroke-dasharray="4,3"/>')
        prior_level = top_value
    text(parts, 70, 380, "Budget reference funded by USAID; values describe one standardized package rather than operating-ledger expenditures.", 12, fill="#555")


def draw_monthly_cash_flow(parts: list[str], monthly: pd.DataFrame) -> None:
    left, top, plot_w, plot_h = 95, 485, 1260, 250
    text(parts, 70, 455, "Panel B — Monthly facility payments, outflows, and cumulative ledger balance", 18, font_weight="bold")
    monthly_max = max(float(monthly["facility_payments_usd"].max()), float(monthly["recorded_outflows_usd"].max()), 1) * 1.12
    cumulative_max = max(float(monthly["cumulative_ledger_balance_usd"].max()), 1) * 1.12
    cell = plot_w / len(monthly); bar_w = cell * 0.72
    for tick in range(4):
        value = monthly_max * tick / 3; y = top + plot_h * (1 - tick / 3)
        parts.append(f'<line x1="{left}" y1="{y}" x2="{left+plot_w}" y2="{y}" stroke="#ececec"/>')
        text(parts, left - 8, y + 4, f"${value:,.0f}", 10, text_anchor="end")
        text(parts, left + plot_w + 8, y + 4, f"${cumulative_max*tick/3:,.0f}", 10)
    points = []
    for index, (_, row) in enumerate(monthly.iterrows()):
        x = left + (index + 0.5) * cell - bar_w / 2; base = top + plot_h
        for code in FACILITY_CODES:
            value = float(row[code]); height = plot_h * value / monthly_max
            parts.append(f'<rect x="{x}" y="{base-height}" width="{bar_w*0.70}" height="{height}" fill="{FACILITY_COLORS[code]}"/>')
            base -= height
        outflow_x = x + bar_w * 0.72; outflow_w = bar_w * 0.28; outflow_base = top + plot_h
        for column, color in (("opex_outflows_usd", "#8c8c8c"), ("capex_outflows_usd", "#17365d")):
            height = plot_h * float(row[column]) / monthly_max
            if height:
                parts.append(f'<rect x="{outflow_x}" y="{outflow_base-height}" width="{outflow_w}" height="{height}" fill="{color}"/>')
                outflow_base -= height
        point_x = left + (index + 0.5) * cell
        point_y = top + plot_h * (1 - float(row["cumulative_ledger_balance_usd"]) / cumulative_max)
        points.append(f"{point_x:.2f},{point_y:.2f}")
    parts.append(f'<polyline points="{" ".join(points)}" fill="none" stroke="#111" stroke-width="3" stroke-dasharray="8,5"/>')
    for index in sorted(set([0, len(monthly)//2, len(monthly)-1])):
        x = left + (index + 0.5) * cell
        text(parts, x, top + plot_h + 20, pd.Timestamp(monthly.index[index]).strftime("%b %Y"), 10, text_anchor="middle")
    legend_y = top + plot_h + 42
    for index, code in enumerate(FACILITY_CODES):
        x = 75 + index * 120; parts.append(f'<rect x="{x}" y="{legend_y}" width="12" height="12" fill="{FACILITY_COLORS[code]}"/>')
        text(parts, x + 18, legend_y + 11, code, 10)
    parts += [f'<rect x="805" y="{legend_y}" width="12" height="12" fill="#8c8c8c"/>',
              f'<rect x="930" y="{legend_y}" width="12" height="12" fill="#17365d"/>',
              f'<line x1="1085" y1="{legend_y+6}" x2="1115" y2="{legend_y+6}" stroke="#111" stroke-width="3" stroke-dasharray="8,5"/>']
    text(parts, 823, legend_y + 11, "OPEX outflow", 10); text(parts, 948, legend_y + 11, "Expansion CAPEX outflow", 10)
    text(parts, 1123, legend_y + 11, "Cumulative balance", 10)


def draw_deployment_capex(parts: list[str], reference: pd.DataFrame) -> None:
    left, top, plot_w, plot_h = 75, 925, 600, 225
    text(parts, 70, 895, "Panel C — Deployment CAPEX and monthly commitment", 17, font_weight="bold")
    maximum = max(reference["deployment_capex_usd"].max(), 1) * 1.12
    commitment_max = max(reference["monthly_commitment_usd"].max(), 1) * 1.12
    cell = plot_w / len(reference); bar_w = cell * 0.55
    for tick in range(4):
        value = maximum * tick / 3; y = top + plot_h * (1 - tick / 3)
        parts.append(f'<line x1="{left}" y1="{y}" x2="{left+plot_w}" y2="{y}" stroke="#ececec"/>')
        text(parts, left - 8, y + 4, f"${value:,.0f}", 10, text_anchor="end")
        text(parts, left + plot_w + 5, y + 4, f"${commitment_max*tick/3:,.0f}", 9)
    for index, row in reference.reset_index(drop=True).iterrows():
        code = row["facility_code"]; x = left + (index + 0.5) * cell
        height = plot_h * row["deployment_capex_usd"] / maximum
        parts.append(f'<rect x="{x-bar_w/2}" y="{top+plot_h-height}" width="{bar_w}" height="{height}" fill="{FACILITY_COLORS[code]}"/>')
        text(parts, x, top + plot_h - height + 14, f'${row["deployment_capex_usd"]:,.0f}', 9,
             text_anchor="middle", fill="#ffffff", font_weight="bold")
        y_point = top + plot_h * (1 - row["monthly_commitment_usd"] / commitment_max)
        parts.append(f'<circle cx="{x}" cy="{y_point}" r="6" fill="#111"/>')
        text(parts, x, y_point - 9, f'${row["monthly_commitment_usd"]:,.0f}/mo', 9, text_anchor="middle")
        text(parts, x, top + plot_h + 18, code, 10, text_anchor="middle")
    text(parts, 70, 1185, "Bars: standardized-package CAPEX. Points: monthly commitment.", 10, fill="#555")


def draw_revenue(parts: list[str], facility: pd.DataFrame) -> None:
    left, top, plot_w, plot_h = 770, 925, 585, 225
    text(parts, 765, 895, "Panel D — Actual payment revenue and timing", 17, font_weight="bold")
    maximum = max(float(facility["received_usd"].max()), 1) * 1.12; cell = plot_w / len(facility); bar_w = cell * 0.55
    for tick in range(4):
        value = maximum * tick / 3; y = top + plot_h * (1 - tick / 3)
        parts.append(f'<line x1="{left}" y1="{y}" x2="{left+plot_w}" y2="{y}" stroke="#ececec"/>')
        text(parts, left - 8, y + 4, f"${value:,.0f}", 10, text_anchor="end")
        text(parts, left + plot_w + 5, y + 4, f"{100*tick/3:.0f}%", 9)
    for index, row in facility.reset_index(drop=True).iterrows():
        code = row["facility_code"]; x = left + (index + 0.5) * cell
        height = plot_h * float(row["received_usd"]) / maximum
        parts.append(f'<rect x="{x-bar_w/2}" y="{top+plot_h-height}" width="{bar_w}" height="{height}" fill="{FACILITY_COLORS[code]}"/>')
        text(parts, x, top + plot_h - height - 7, f'${row["received_usd"]:,.0f}', 9, text_anchor="middle")
        y_point = top + plot_h * (1 - float(row["on_time_pct"]) / 100)
        parts.append(f'<circle cx="{x}" cy="{y_point}" r="6" fill="#111"/>')
        text(parts, x, y_point - 9, f'{row["on_time_pct"]:.1f}%', 9, text_anchor="middle")
        text(parts, x, top + plot_h + 18, code, 10, text_anchor="middle")
    text(parts, 765, 1185, "Bars: revenue received. Points: share recorded on time.", 10, fill="#555")


def write_figure(path: Path, components: pd.DataFrame, monthly: pd.DataFrame,
                 reference: pd.DataFrame, facility: pd.DataFrame) -> None:
    width, height = 1450, 1210
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
             '<rect width="100%" height="100%" fill="white"/>']
    text(parts, width / 2, 31, "Capital investment and facility payment performance", 23,
         text_anchor="middle", font_weight="bold")
    draw_package_waterfall(parts, components)
    draw_monthly_cash_flow(parts, monthly)
    draw_deployment_capex(parts, reference)
    draw_revenue(parts, facility)
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
    reference = pd.read_csv(PROJECT_ROOT / "config" / "facility_financial_reference.csv")
    facility = facility_payment_summary(data); facility.to_csv(output / "facility_payment_summary.csv", index=False)
    overall_payment_summary(data).to_csv(output / "overall_payment_summary.csv", index=False)
    monthly = monthly_cash_flow(data); monthly.to_csv(output / "monthly_cash_flow.csv")
    outflows = outflows_by_facility_category(data); outflows.to_csv(output / "outflows_by_facility_and_category.csv")
    reference.to_csv(output / "facility_capex_and_commitment.csv", index=False)
    subsequent_capex = outflows[[column for column in outflows.columns if column in SUBSEQUENT_CAPEX_CATEGORIES]]
    subsequent_capex.to_csv(output / "subsequent_capex_by_facility.csv")
    write_figure(output / "figure6_capex_and_payments.svg", components, monthly, reference, facility)
    print(f"payments: {len(data)} ledger rows, ${facility['received_usd'].sum():,.0f} received")


if __name__ == "__main__":
    main()
