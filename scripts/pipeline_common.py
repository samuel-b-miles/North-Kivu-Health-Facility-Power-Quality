"""Shared path and output helpers for executable analysis scripts."""

from __future__ import annotations

import csv
import html
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RAW_ROOT = PROJECT_ROOT / "data" / "raw" / "extracted"
DEFAULT_OUTPUT_ROOT = PROJECT_ROOT / "outputs" / "generated"


def read_config(name: str) -> list[dict[str, str]]:
    with (PROJECT_ROOT / "config" / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def apply_primary_telemetry_window(frame: pd.DataFrame, facility_code: str, time_column: str = "time") -> pd.DataFrame:
    """Apply confirmed post-monitoring starts and telemetry exclusions."""
    data = frame.copy()
    data[time_column] = pd.to_datetime(data[time_column], errors="coerce", utc=True)
    periods = [row for row in read_config("analysis_periods.csv") if row["facility_code"] == facility_code]
    starts = [row for row in periods if row["period_type"] == "powerwatch_post_source_start"]
    if len(starts) != 1:
        raise ValueError(f"Expected one PowerWatch post-source start for {facility_code}; found {len(starts)}")
    start = pd.Timestamp(starts[0]["start_date"], tz="UTC")
    data = data[data[time_column] >= start]
    for row in periods:
        if row["period_type"] != "telemetry_exclusion":
            continue
        exclusion_start = pd.Timestamp(row["start_date"], tz="UTC")
        if row["end_date"]:
            # Dates are inclusive in configuration; advance one day for filtering.
            exclusion_end = pd.Timestamp(row["end_date"], tz="UTC") + pd.Timedelta(days=1)
            data = data[~((data[time_column] >= exclusion_start) & (data[time_column] < exclusion_end))]
        else:
            data = data[data[time_column] < exclusion_start]
    return data.sort_values(time_column)


def telemetry_exclusions(facility_code: str) -> list[tuple[pd.Timestamp, pd.Timestamp | None]]:
    """Return exclusion intervals with an exclusive upper bound for bin counting."""
    return [(pd.Timestamp(row["start_date"], tz="UTC"),
             pd.Timestamp(row["end_date"], tz="UTC") + pd.Timedelta(days=1) if row["end_date"] else None)
            for row in read_config("analysis_periods.csv")
            if row["facility_code"] == facility_code and row["period_type"] == "telemetry_exclusion"]


def find_powerwatch(raw_root: Path, sensor_id: str, preferred: str = "") -> Path:
    candidates = [p for p in raw_root.rglob(f"{sensor_id}*.csv") if "power_quality" not in p.name and "data_quality" not in p.name]
    if preferred == "updated":
        candidates = [p for p in candidates if "updated" in p.name.lower()]
    elif preferred == "original":
        candidates = [p for p in candidates if "_og" in p.name.lower()]
    if len(candidates) != 1:
        raise FileNotFoundError(f"Expected one PowerWatch file for {sensor_id} ({preferred}); found {candidates}")
    return candidates[0]


def find_hop_voltage(raw_root: Path, sensor_id: str) -> Path:
    candidates = list(raw_root.rglob(f"*{sensor_id}*Voltage*.csv"))
    if len(candidates) != 1:
        raise FileNotFoundError(f"Expected one HOP voltage file for {sensor_id}; found {candidates}")
    return candidates[0]


def find_hop_energy(raw_root: Path, sensor_id: str) -> Path:
    candidates = list(raw_root.rglob(f"*{sensor_id}*energy_per_day.csv*"))
    if len(candidates) != 1:
        raise FileNotFoundError(f"Expected one HOP daily-energy file for {sensor_id}; found {candidates}")
    return candidates[0]


def write_bar_svg(path: Path, labels: list[str], values: list[float], title: str, ylabel: str) -> None:
    width, height, left, top, bottom = 1000, 560, 90, 70, 120
    plot_w, plot_h = width - left - 30, height - top - bottom
    bar_w = plot_w / max(len(values), 1) * 0.65
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
             '<rect width="100%" height="100%" fill="white"/>',
             f'<text x="{width/2}" y="35" text-anchor="middle" font-family="sans-serif" font-size="22">{html.escape(title)}</text>']
    for tick in range(0, 101, 20):
        y = top + plot_h * (1 - tick / 100)
        parts += [f'<line x1="{left}" y1="{y}" x2="{width-30}" y2="{y}" stroke="#dddddd"/>',
                  f'<text x="{left-10}" y="{y+5}" text-anchor="end" font-family="sans-serif" font-size="13">{tick}</text>']
    for index, (label, value) in enumerate(zip(labels, values)):
        x = left + (index + 0.5) * plot_w / len(values) - bar_w / 2
        bar_h = plot_h * max(0, min(100, float(value))) / 100
        y = top + plot_h - bar_h
        parts += [f'<rect x="{x}" y="{y}" width="{bar_w}" height="{bar_h}" fill="#2b8cbe"/>',
                  f'<text x="{x+bar_w/2}" y="{y-7}" text-anchor="middle" font-family="sans-serif" font-size="12">{value:.2f}</text>',
                  f'<text x="{x+bar_w/2}" y="{top+plot_h+24}" text-anchor="middle" font-family="sans-serif" font-size="12">{html.escape(label)}</text>']
    parts += [f'<text transform="translate(22 {top+plot_h/2}) rotate(-90)" text-anchor="middle" font-family="sans-serif" font-size="14">{html.escape(ylabel)}</text>', '</svg>']
    path.write_text("\n".join(parts), encoding="utf-8")


def write_stacked_svg(path: Path, frame: pd.DataFrame, title: str) -> None:
    width, height, left, top, bottom = 1100, 620, 90, 70, 90
    plot_w, plot_h = width - left - 40, height - top - bottom
    values = frame.fillna(0).astype(float)
    total = values.sum(axis=1); maximum = float(total.max()) or 1.0
    x_values = [left + plot_w * i / max(len(values) - 1, 1) for i in range(len(values))]
    lower = pd.Series(0.0, index=values.index)
    colors = ["#2b8cbe", "#31a354", "#fdae6b", "#756bb1", "#de2d26", "#636363"]
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
             '<rect width="100%" height="100%" fill="white"/>',
             f'<text x="{width/2}" y="35" text-anchor="middle" font-family="sans-serif" font-size="22">{html.escape(title)}</text>']
    for index, column in enumerate(values.columns):
        upper = lower + values[column]
        top_points = [(x, top + plot_h * (1 - y / maximum)) for x, y in zip(x_values, upper)]
        bottom_points = [(x, top + plot_h * (1 - y / maximum)) for x, y in zip(reversed(x_values), reversed(lower.tolist()))]
        points = " ".join(f"{x:.1f},{y:.1f}" for x, y in top_points + bottom_points)
        color = colors[index % len(colors)]
        parts.append(f'<polygon points="{points}" fill="{color}" fill-opacity="0.85"/>')
        parts.append(f'<rect x="{left+index*145}" y="{height-35}" width="16" height="16" fill="{color}"/><text x="{left+20+index*145}" y="{height-22}" font-family="sans-serif" font-size="13">{html.escape(str(column))}</text>')
        lower = upper
    parts += [f'<line x1="{left}" y1="{top+plot_h}" x2="{width-40}" y2="{top+plot_h}" stroke="black"/>',
              f'<text transform="translate(22 {top+plot_h/2}) rotate(-90)" text-anchor="middle" font-family="sans-serif" font-size="14">Cumulative energy (kWh)</text>', '</svg>']
    path.write_text("\n".join(parts), encoding="utf-8")


def write_value_bar_svg(path: Path, labels: list[str], values: list[float], title: str, ylabel: str) -> None:
    width, height, left, top, bottom = 1000, 560, 100, 70, 100
    plot_w, plot_h = width - left - 30, height - top - bottom
    maximum = max(values) * 1.12 if values else 1.0
    bar_w = plot_w / max(len(values), 1) * 0.65
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
             '<rect width="100%" height="100%" fill="white"/>',
             f'<text x="{width/2}" y="35" text-anchor="middle" font-family="sans-serif" font-size="22">{html.escape(title)}</text>']
    for step in range(6):
        value = maximum * step / 5
        y = top + plot_h * (1 - step / 5)
        parts += [f'<line x1="{left}" y1="{y}" x2="{width-30}" y2="{y}" stroke="#dddddd"/>',
                  f'<text x="{left-10}" y="{y+5}" text-anchor="end" font-family="sans-serif" font-size="12">{value:,.0f}</text>']
    for index, (label, value) in enumerate(zip(labels, values)):
        x = left + (index + 0.5) * plot_w / len(values) - bar_w / 2
        bar_h = plot_h * float(value) / maximum
        y = top + plot_h - bar_h
        parts += [f'<rect x="{x}" y="{y}" width="{bar_w}" height="{bar_h}" fill="#f28e2b"/>',
                  f'<text x="{x+bar_w/2}" y="{y-7}" text-anchor="middle" font-family="sans-serif" font-size="12">{value:,.1f}</text>',
                  f'<text x="{x+bar_w/2}" y="{top+plot_h+24}" text-anchor="middle" font-family="sans-serif" font-size="13">{html.escape(label)}</text>']
    parts += [f'<text transform="translate(22 {top+plot_h/2}) rotate(-90)" text-anchor="middle" font-family="sans-serif" font-size="14">{html.escape(ylabel)}</text>', '</svg>']
    path.write_text("\n".join(parts), encoding="utf-8")


def write_monthly_facility_panels_svg(
    path: Path, frame: pd.DataFrame, telemetry_exclusions: list[dict[str, str]] | None = None
) -> None:
    """Write six comparable monthly-consumption panels using anonymized facility codes."""
    facility_order = ["HGR1", "CH1", "CSR1", "CSR2", "CSR3", "CSR4"]
    columns = [code for code in facility_order if code in frame.columns]
    columns.extend([code for code in frame.columns if code not in columns])
    width, height = 1500, 850
    outer_left, outer_top, panel_w, panel_h = 85, 75, 420, 290
    col_gap, row_gap = 70, 95
    plot_left, plot_top, plot_w, plot_h = 58, 35, 345, 205
    maximum = max(float(frame.max().max()), 1.0) * 1.08
    colors = {
        "HGR1": "#edc948",
        "CH1": "#2b8cbe",
        "CSR1": "#f28e2b",
        "CSR2": "#59a14f",
        "CSR3": "#e78ac3",
        "CSR4": "#756bb1",
    }
    telemetry_exclusions = telemetry_exclusions or []
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
             '<defs><pattern id="telemetry-hatch" width="10" height="10" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><rect width="10" height="10" fill="#d9d9d9" fill-opacity="0.72"/><line x1="0" y1="0" x2="0" y2="10" stroke="#888" stroke-width="3"/></pattern></defs>',
             '<rect width="100%" height="100%" fill="white"/>',
             f'<text x="{width/2}" y="34" text-anchor="middle" font-family="sans-serif" font-size="22" font-weight="bold">Monthly monitored electricity consumption by facility</text>']
    for index, column in enumerate(columns):
        row, col = divmod(index, 3)
        x0 = outer_left + col * (panel_w + col_gap); y0 = outer_top + row * (panel_h + row_gap)
        px, py = x0 + plot_left, y0 + plot_top
        values = frame[column].fillna(0).astype(float).tolist()
        bar_w = plot_w / max(len(values), 1) * 0.82
        parts.append(f'<text x="{x0+panel_w/2}" y="{y0+18}" text-anchor="middle" font-family="sans-serif" font-size="17" font-weight="bold">{html.escape(str(column))}</text>')
        for tick in range(5):
            value = maximum * tick / 4; y = py + plot_h * (1 - tick / 4)
            parts += [f'<line x1="{px}" y1="{y}" x2="{px+plot_w}" y2="{y}" stroke="#e5e5e5"/>',
                      f'<text x="{px-7}" y="{y+4}" text-anchor="end" font-family="sans-serif" font-size="10">{value:.0f}</text>']
        for j, value in enumerate(values):
            x = px + j * plot_w / max(len(values), 1) + (plot_w / max(len(values), 1) - bar_w) / 2
            bar_h = plot_h * value / maximum; y = py + plot_h - bar_h
            fill = colors.get(str(column), "#777777")
            parts.append(f'<rect x="{x:.2f}" y="{y:.2f}" width="{bar_w:.2f}" height="{bar_h:.2f}" fill="{fill}"/>')
        # Overlay continuous hatched bands for confirmed periods without reliable
        # telemetry. These are missing-measurement periods, not inferred outages.
        for exclusion in [e for e in telemetry_exclusions if e["facility_code"] == column]:
            exclusion_start = pd.Timestamp(exclusion["start_date"], tz="UTC")
            exclusion_end = (pd.Timestamp(exclusion["end_date"], tz="UTC") + pd.Timedelta(days=1)
                             if exclusion["end_date"] else pd.Timestamp(frame.index[-1]) + pd.offsets.MonthBegin(1))
            for j, month_start in enumerate(pd.DatetimeIndex(frame.index)):
                month_end = month_start + pd.offsets.MonthBegin(1)
                overlap_start = max(month_start, exclusion_start); overlap_end = min(month_end, exclusion_end)
                if overlap_start >= overlap_end:
                    continue
                cell_x = px + j * plot_w / len(values); cell_w = plot_w / len(values)
                start_fraction = (overlap_start - month_start) / (month_end - month_start)
                end_fraction = (overlap_end - month_start) / (month_end - month_start)
                shade_x = cell_x + cell_w * float(start_fraction)
                shade_w = cell_w * float(end_fraction - start_fraction)
                parts.append(f'<rect x="{shade_x:.2f}" y="{py}" width="{shade_w:.2f}" height="{plot_h}" fill="url(#telemetry-hatch)" stroke="none"/>')
        parts += [f'<line x1="{px}" y1="{py+plot_h}" x2="{px+plot_w}" y2="{py+plot_h}" stroke="#444"/>',
                  f'<text transform="translate({x0+12} {py+plot_h/2}) rotate(-90)" text-anchor="middle" font-family="sans-serif" font-size="12">kWh</text>']
        if len(frame.index):
            tick_positions = sorted(set([0, len(frame.index)//2, len(frame.index)-1]))
            for j in tick_positions:
                x = px + (j + 0.5) * plot_w / len(frame.index)
                label = pd.Timestamp(frame.index[j]).strftime("%b %Y")
                parts.append(f'<text x="{x:.1f}" y="{py+plot_h+20}" text-anchor="middle" font-family="sans-serif" font-size="10">{label}</text>')
    parts += [f'<rect x="{width/2-245}" y="{height-39}" width="22" height="13" fill="url(#telemetry-hatch)"/>',
              f'<text x="{width/2-215}" y="{height-28}" font-family="sans-serif" font-size="12" fill="#555">Confirmed unreliable or unavailable telemetry (not inferred system outage)</text>', '</svg>']
    path.write_text("\n".join(parts), encoding="utf-8")


def write_pre_post_triptych_svg(path: Path, rows: list[dict[str, object]], *, source_comparison: bool = False) -> None:
    width, height = 1500, 580 if source_comparison else 520
    margin_x, top, plot_h, panel_w, gap = 70, 65, 380, 420, 60
    metrics = [
        ("uptime_pre_pct", "uptime_post_pct", "Power uptime (%)"),
        ("voltage_pre_pct", "voltage_post_pct", "Voltage compliance (±10%, 230 V)"),
        ("frequency_5_pre_pct", "frequency_5_post_pct", "Frequency compliance (±5%, 50 Hz)"),
    ]
    colors = {
        "CH1": "#2b8cbe",
        "CSR1": "#f28e2b",
        "CSR2": "#59a14f",
        "CSR3": "#e78ac3",
        "CSR4": "#756bb1",
        "HGR1": "#edc948",
    }
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
             '<rect width="100%" height="100%" fill="white"/>']
    for panel, (pre_key, post_key, title) in enumerate(metrics):
        x0 = margin_x + panel * (panel_w + gap)
        x_pre, x_post = x0 + 115, x0 + 315
        parts.append(f'<text x="{x0+panel_w/2}" y="28" text-anchor="middle" font-family="sans-serif" font-size="19" font-weight="bold">{html.escape(title)}</text>')
        for tick in range(0, 101, 20):
            y = top + plot_h * (1 - tick / 100)
            parts.append(f'<line x1="{x0}" y1="{y}" x2="{x0+panel_w}" y2="{y}" stroke="#e6e6e6"/>')
            if panel == 0:
                parts.append(f'<text x="{x0-8}" y="{y+5}" text-anchor="end" font-family="sans-serif" font-size="12">{tick}%</text>')
        # Cohort distribution boxplots sit behind facility trajectories.
        for x_position, key in ((x_pre, pre_key), (x_post, post_key)):
            distribution = pd.Series([float(row[key]) for row in rows])
            minimum = float(distribution.min()); q1 = float(distribution.quantile(0.25))
            median = float(distribution.median()); q3 = float(distribution.quantile(0.75)); maximum = float(distribution.max())
            y_min = top + plot_h * (1 - minimum / 100); y_q1 = top + plot_h * (1 - q1 / 100)
            y_median = top + plot_h * (1 - median / 100); y_q3 = top + plot_h * (1 - q3 / 100)
            y_max = top + plot_h * (1 - maximum / 100); box_width = 66
            parts += [
                f'<line x1="{x_position}" y1="{y_max}" x2="{x_position}" y2="{y_min}" stroke="#9e9e9e" stroke-width="2"/>',
                f'<line x1="{x_position-15}" y1="{y_max}" x2="{x_position+15}" y2="{y_max}" stroke="#9e9e9e" stroke-width="2"/>',
                f'<line x1="{x_position-15}" y1="{y_min}" x2="{x_position+15}" y2="{y_min}" stroke="#9e9e9e" stroke-width="2"/>',
                f'<rect x="{x_position-box_width/2}" y="{y_q3}" width="{box_width}" height="{max(y_q1-y_q3,1)}" fill="#d9d9d9" fill-opacity="0.65" stroke="#9e9e9e"/>',
                f'<line x1="{x_position-box_width/2}" y1="{y_median}" x2="{x_position+box_width/2}" y2="{y_median}" stroke="#555555" stroke-width="3"/>',
            ]
        for index, row in enumerate(rows):
            pre, post = float(row[pre_key]), float(row[post_key])
            y_pre = top + plot_h * (1 - pre / 100); y_post = top + plot_h * (1 - post / 100)
            color = colors.get(str(row["facility_code"]), "#666666")
            parts += [f'<line x1="{x_pre}" y1="{y_pre}" x2="{x_post}" y2="{y_post}" stroke="{color}" stroke-width="3"/>',
                      f'<circle cx="{x_pre}" cy="{y_pre}" r="5" fill="{color}"/>',
                      f'<circle cx="{x_post}" cy="{y_post}" r="5" fill="{color}"/>']
        left_label = "Existing supply" if source_comparison else "Pre"
        right_label = "Protected circuit" if source_comparison else "Post"
        parts += [f'<text x="{x_pre}" y="{top+plot_h+28}" text-anchor="middle" font-family="sans-serif" font-size="14">{left_label}</text>',
                  f'<text x="{x_post}" y="{top+plot_h+28}" text-anchor="middle" font-family="sans-serif" font-size="14">{right_label}</text>']
    legend_y = height - 80 if source_comparison else height - 20
    for index, row in enumerate(rows):
        x = 120 + index * 205; color = colors.get(str(row["facility_code"]), "#666666")
        label = str(row["facility_code"])
        if source_comparison:
            label += " *" if row.get("baseline_sensor_basis") == "single_powerwatch" else " †"
        parts += [f'<line x1="{x}" y1="{legend_y}" x2="{x+24}" y2="{legend_y}" stroke="{color}" stroke-width="3"/>',
                  f'<text x="{x+30}" y="{legend_y+5}" font-family="sans-serif" font-size="13">{html.escape(label)}</text>']
    if source_comparison:
        policy = str(rows[0].get("pqr_denominator_policy", "joint"))
        note = "PQR: jointly valid voltage/frequency readings." if policy == "joint" else "PQR: separate voltage and frequency denominators (sensitivity)."
        parts += [f'<text x="70" y="538" font-family="sans-serif" font-size="12">* Reconstructed single-PowerWatch source comparisons; † inherited baseline values awaiting reconstruction.</text>',
                  f'<text x="70" y="558" font-family="sans-serif" font-size="12">Follow-up uptime: paired HOP/PowerWatch, expected-window denominator. {note}</text>']
    parts.append('</svg>')
    path.write_text("\n".join(parts), encoding="utf-8")
