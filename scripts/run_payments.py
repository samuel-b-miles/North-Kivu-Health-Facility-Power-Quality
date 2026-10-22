#!/usr/bin/env python3
"""Generate CAPEX, payment-revenue, and payment-timing manuscript outputs."""

from __future__ import annotations

import argparse
import html
from pathlib import Path
import shutil

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
    "CH1": "#2b8cbe", "CSR1": "#f28e2b", "CSR2": "#59a14f",
    "CSR3": "#e78ac3", "CSR4": "#756bb1", "HGR1": "#edc948",
}


def text(parts: list[str], x: float, y: float, value: str, size: int = 18, **attrs: str) -> None:
    options = " ".join(f'{key.replace("_", "-")}="{html.escape(str(val))}"' for key, val in attrs.items())
    parts.append(f'<text x="{x}" y="{y}" font-family="Arial" font-size="{size}" {options}>{html.escape(value)}</text>')


def standard_package_steps(components: pd.DataFrame) -> list[tuple[str, float, str]]:
    amount = components.set_index("component")["amount_usd"]
    equipment = components.loc[components["cost_group"] == "equipment", "amount_usd"].sum()
    freight_agent = amount["Ocean freight"] + amount["Import agent and documentation"]
    duties_port = amount["Import duties"] + amount["CIF port and other duties"]
    return [
        ("Equipment\nsubtotal", equipment, "total"),
        ("Freight +\nagent", freight_agent, "step"),
        ("Duties +\nport", duties_port, "step"),
        ("VAT", amount["VAT"], "step"),
        ("Delivery +\ninstallation", amount["In-country delivery and installation"], "step"),
        ("Installed\npackage", components["amount_usd"].sum(), "total"),
    ]


def draw_package_waterfall(parts: list[str], components: pd.DataFrame) -> None:
    left, top, plot_w, plot_h = 130, 110, 1340, 235
    text(parts, 65, 78, "Panel A — Standard reference package CAPEX", 23, font_weight="bold")
    steps = standard_package_steps(components); maximum = steps[-1][1] * 1.10
    cell = plot_w / len(steps); bar_w = cell * 0.62; running = 0.0
    step_colors = ["#334155", "#64748b", "#94a3b8", "#b6a6ca", "#8b6f47", "#0f766e"]
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
        text(parts, x + bar_w / 2, y_top - 9, f"${value:,.0f}", 17, text_anchor="middle", font_weight="bold")
        for line_number, line in enumerate(label.split("\n")):
            text(parts, x + bar_w / 2, top + plot_h + 22 + 19 * line_number, line, 16, text_anchor="middle")
        if index and kind == "step":
            y = top + plot_h * (1 - prior_level / maximum)
            previous_x = left + (index - 0.5) * cell + bar_w / 2
            parts.append(f'<line x1="{previous_x}" y1="{y}" x2="{x}" y2="{y}" stroke="#888" stroke-dasharray="4,3"/>')
        prior_level = top_value
    text(parts, 65, 420, "USAID-funded budget reference; one standardized package.", 17, fill="#444")


def draw_monthly_cash_flow(parts: list[str], monthly: pd.DataFrame) -> None:
    left, top, plot_w, plot_h = 130, 1030, 1300, 260
    text(parts, 65, 990, "Panel D — Monthly payments, outflows, and cumulative balance", 22, font_weight="bold")
    monthly_max = max(float(monthly["facility_payments_usd"].max()), float(monthly["recorded_outflows_usd"].max()), 1) * 1.12
    cumulative_max = max(float(monthly["cumulative_ledger_balance_usd"].max()), 1) * 1.12
    cell = plot_w / len(monthly); bar_w = cell * 0.72
    for tick in range(4):
        value = monthly_max * tick / 3; y = top + plot_h * (1 - tick / 3)
        parts.append(f'<line x1="{left}" y1="{y}" x2="{left+plot_w}" y2="{y}" stroke="#ececec"/>')
        text(parts, left - 9, y + 6, f"${value:,.0f}", 18, text_anchor="end")
        text(parts, left + plot_w + 8, y + 6, f"${cumulative_max*tick/3:,.0f}", 17)
    text(parts, left - 105, top + plot_h / 2, "Monthly cash flow (USD)", 20,
         text_anchor="middle", transform=f"rotate(-90 {left - 105} {top + plot_h / 2})")
    text(parts, left + plot_w + 95, top + plot_h / 2, "Cumulative balance (USD)", 18,
         text_anchor="middle", transform=f"rotate(90 {left + plot_w + 95} {top + plot_h / 2})")
    points = []
    for index, (_, row) in enumerate(monthly.iterrows()):
        x = left + (index + 0.5) * cell - bar_w / 2; base = top + plot_h
        for code in FACILITY_CODES:
            value = float(row[code]); height = plot_h * value / monthly_max
            parts.append(f'<rect x="{x}" y="{base-height}" width="{bar_w*0.70}" height="{height}" fill="{FACILITY_COLORS[code]}"/>')
            base -= height
        outflow_x = x + bar_w * 0.72; outflow_w = bar_w * 0.28; outflow_base = top + plot_h
        for column, color in (("opex_outflows_usd", "#6b7280"), ("capex_outflows_usd", "#9c2f2f")):
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
        text(parts, x, top + plot_h + 25, pd.Timestamp(monthly.index[index]).strftime("%b %Y"), 18, text_anchor="middle")
    legend_y = top + plot_h + 54
    for index, code in enumerate(FACILITY_CODES):
        col, row = index % 3, index // 3; x = 130 + col * 190; y = legend_y + row * 24
        parts.append(f'<rect x="{x}" y="{y}" width="16" height="16" fill="{FACILITY_COLORS[code]}"/>')
        text(parts, x + 22, y + 15, code, 18)
    parts += [f'<rect x="800" y="{legend_y}" width="16" height="16" fill="#6b7280"/>',
              f'<rect x="800" y="{legend_y+24}" width="16" height="16" fill="#9c2f2f"/>',
              f'<line x1="1220" y1="{legend_y+8}" x2="1250" y2="{legend_y+8}" stroke="#111" stroke-width="3" stroke-dasharray="8,5"/>']
    text(parts, 822, legend_y + 15, "OPEX", 17); text(parts, 822, legend_y + 39, "Expansion CAPEX", 17)
    text(parts, 1260, legend_y + 15, "Balance", 17)


def draw_deployment_capex(parts: list[str], reference: pd.DataFrame) -> None:
    left, top, plot_w, plot_h = 130, 550, 535, 260
    text(parts, 65, 490, "Panel B — Deployment CAPEX and", 23, font_weight="bold")
    text(parts, 65, 520, "monthly commitment", 23, font_weight="bold")
    maximum = max(reference["deployment_capex_usd"].max(), 1) * 1.12
    commitment_max = max(reference["monthly_commitment_usd"].max(), 1) * 1.12
    cell = plot_w / len(reference); bar_w = cell * 0.55
    for tick in range(4):
        value = maximum * tick / 3; y = top + plot_h * (1 - tick / 3)
        parts.append(f'<line x1="{left}" y1="{y}" x2="{left+plot_w}" y2="{y}" stroke="#ececec"/>')
        text(parts, left - 8, y + 6, f"${value:,.0f}", 18, text_anchor="end")
        text(parts, left + plot_w + 5, y + 6, f"${commitment_max*tick/3:,.0f}", 17)
    text(parts, left - 105, top + plot_h / 2, "Deployment CAPEX (USD)", 20,
         text_anchor="middle", transform=f"rotate(-90 {left - 105} {top + plot_h / 2})")
    text(parts, left + plot_w + 95, top + plot_h / 2, "Monthly commitment (USD)", 20,
         text_anchor="middle", transform=f"rotate(90 {left + plot_w + 95} {top + plot_h / 2})")
    for index, row in reference.reset_index(drop=True).iterrows():
        code = row["facility_code"]; x = left + (index + 0.5) * cell
        height = plot_h * row["deployment_capex_usd"] / maximum
        parts.append(f'<rect x="{x-bar_w/2}" y="{top+plot_h-height}" width="{bar_w}" height="{height}" fill="{FACILITY_COLORS[code]}"/>')
        text(parts, x, top + plot_h - 15, f'${row["deployment_capex_usd"]:,.0f}', 15,
             text_anchor="middle", fill="#ffffff", font_weight="bold")
        y_point = top + plot_h * (1 - row["monthly_commitment_usd"] / commitment_max)
        parts.append(f'<circle cx="{x}" cy="{y_point}" r="6" fill="#111"/>')
        text(parts, x, y_point - 16, f'${row["monthly_commitment_usd"]:,.0f}/mo', 16, text_anchor="middle")
        text(parts, x, top + plot_h + 24, code, 19, text_anchor="middle")
    text(parts, 65, 880, "Bars: standardized-package CAPEX. Points: monthly commitment.", 17, fill="#444")


def draw_revenue(parts: list[str], facility: pd.DataFrame) -> None:
    left, top, plot_w, plot_h = 920, 550, 515, 260
    text(parts, 845, 520, "Panel C — Actual payment revenue and timing", 23, font_weight="bold")
    maximum = max(float(facility["received_usd"].max()), 1) * 1.12; cell = plot_w / len(facility); bar_w = cell * 0.55
    for tick in range(4):
        value = maximum * tick / 3; y = top + plot_h * (1 - tick / 3)
        parts.append(f'<line x1="{left}" y1="{y}" x2="{left+plot_w}" y2="{y}" stroke="#ececec"/>')
        text(parts, left - 8, y + 6, f"${value:,.0f}", 18, text_anchor="end")
        text(parts, left + plot_w + 5, y + 6, f"{100*tick/3:.0f}%", 17)
    text(parts, left - 100, top + plot_h / 2, "Revenue received (USD)", 20,
         text_anchor="middle", transform=f"rotate(-90 {left - 100} {top + plot_h / 2})")
    text(parts, left + plot_w + 95, top + plot_h / 2, "On-time remittances (%)", 20,
         text_anchor="middle", transform=f"rotate(90 {left + plot_w + 95} {top + plot_h / 2})")
    for index, row in facility.reset_index(drop=True).iterrows():
        code = row["facility_code"]; x = left + (index + 0.5) * cell
        height = plot_h * float(row["received_usd"]) / maximum
        parts.append(f'<rect x="{x-bar_w/2}" y="{top+plot_h-height}" width="{bar_w}" height="{height}" fill="{FACILITY_COLORS[code]}"/>')
        text(parts, x, top + plot_h - height - 9, f'${row["received_usd"]:,.0f}', 16, text_anchor="middle")
        y_point = top + plot_h * (1 - float(row["on_time_pct"]) / 100)
        parts.append(f'<circle cx="{x}" cy="{y_point}" r="6" fill="#111"/>')
        text(parts, x, y_point - 10, f'{row["on_time_pct"]:.1f}%', 16, text_anchor="middle")
        text(parts, x, top + plot_h + 24, code, 19, text_anchor="middle")
    text(parts, 845, 880, "Bars: revenue received. Points: share recorded on time.", 17, fill="#444")


def write_figure(path: Path, components: pd.DataFrame, monthly: pd.DataFrame,
                 reference: pd.DataFrame, facility: pd.DataFrame) -> None:
    width, height = 1600, 1420
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
             '<rect width="100%" height="100%" fill="white"/>']
    text(parts, width / 2, 34, "Capital investment and facility payment performance", 31,
         text_anchor="middle", font_weight="bold")
    # Reading order: full-width A, middle-row B/C, full-width D.
    draw_package_waterfall(parts, components)
    draw_deployment_capex(parts, reference)
    draw_revenue(parts, facility)
    draw_monthly_cash_flow(parts, monthly)
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
    figure5 = output / "figure5_capex_and_payments.svg"
    write_figure(figure5, components, monthly, reference, facility)
    # Preserve the historical filename for downstream users of this repository.
    shutil.copyfile(figure5, output / "figure6_capex_and_payments.svg")
    print(f"payments: {len(data)} ledger rows, ${facility['received_usd'].sum():,.0f} received")


if __name__ == "__main__":
    main()
