#!/usr/bin/env python3
"""Generate the manuscript Figure 3 top-panel CSR1 pre/post time series."""

from __future__ import annotations

import argparse
import html
from pathlib import Path

import pandas as pd

from pipeline_common import DEFAULT_OUTPUT_ROOT, DEFAULT_RAW_ROOT, find_powerwatch


FIGURE_START = pd.Timestamp("2024-04-27T00:00:00Z")
FIGURE_END = pd.Timestamp("2024-06-18T23:59:59Z")
INTERVENTION_DATE = pd.Timestamp("2024-05-16T00:00:00Z")


def _load_powerwatch(raw_root: Path, sensor_id: str) -> pd.DataFrame:
    path = find_powerwatch(raw_root, sensor_id, preferred="original")
    frame = pd.read_csv(path)
    frame["time"] = pd.to_datetime(frame["time"], errors="coerce", utc=True)
    frame = frame[(frame["time"] >= FIGURE_START) & (frame["time"] <= FIGURE_END)].copy()
    return frame.sort_values("time")


def _display_sample(frame: pd.DataFrame, keep_outages: bool = False) -> pd.DataFrame:
    data = frame.set_index("time").sort_index()

    def voltage_bin(series: pd.Series) -> float:
        values = pd.to_numeric(series, errors="coerce").dropna()
        if values.empty:
            return float("nan")
        if keep_outages and (values <= 23).any():
            return 0.0
        return float(values.median())

    sampled = data.resample("20min").agg({"voltage": voltage_bin, "frequency": "median"})
    sampled = sampled.dropna(how="all").reset_index()
    return sampled


def _x_scale(ts: pd.Timestamp, left: float, width: float) -> float:
    total = (FIGURE_END - FIGURE_START).total_seconds()
    return left + width * ((ts - FIGURE_START).total_seconds() / total)


def _y_scale(value: float, ymin: float, ymax: float, top: float, height: float) -> float:
    return top + height * (1 - ((value - ymin) / (ymax - ymin)))


def _points(
    frame: pd.DataFrame,
    y_column: str,
    left: float,
    width: float,
    top: float,
    height: float,
    ymin: float,
    ymax: float,
) -> list[tuple[float, float]]:
    points: list[tuple[float, float]] = []
    for row in frame.itertuples():
        value = getattr(row, y_column)
        if pd.isna(value):
            continue
        points.append((_x_scale(row.time, left, width), _y_scale(float(value), ymin, ymax, top, height)))
    return points


def _circle_parts(points: list[tuple[float, float]], color: str, radius: float, opacity: float) -> list[str]:
    return [
        f'<circle cx="{x:.2f}" cy="{y:.2f}" r="{radius}" fill="{color}" fill-opacity="{opacity}"/>'
        for x, y in points
    ]


def _polyline(points: list[tuple[float, float]], color: str, width: float, opacity: float) -> str:
    if not points:
        return ""
    text = " ".join(f"{x:.2f},{y:.2f}" for x, y in points)
    return (
        f'<polyline points="{text}" fill="none" stroke="{color}" '
        f'stroke-width="{width}" stroke-opacity="{opacity}" stroke-linejoin="round" stroke-linecap="round"/>'
    )


def _axis_panel(
    parts: list[str],
    panel_id: str,
    y_label: str,
    y_min: float,
    y_max: float,
    y_ticks: list[float],
    left: float,
    top: float,
    width: float,
    height: float,
) -> None:
    parts.append(f'<g id="{panel_id}">')
    parts.append(f'<rect x="{left}" y="{top}" width="{width}" height="{height}" fill="white"/>')
    for tick in y_ticks:
        y = _y_scale(tick, y_min, y_max, top, height)
        parts.append(f'<line x1="{left}" y1="{y:.2f}" x2="{left + width}" y2="{y:.2f}" stroke="#e7e7e7" stroke-width="1"/>')
        parts.append(
            f'<text x="{left - 16}" y="{y + 5:.2f}" text-anchor="end" '
            'font-family="Arial, Helvetica, sans-serif" font-size="20" fill="#333">'
            f'{tick:g}</text>'
        )
    tick_dates = [
        pd.Timestamp("2024-04-29T00:00:00Z"),
        pd.Timestamp("2024-05-06T00:00:00Z"),
        pd.Timestamp("2024-05-13T00:00:00Z"),
        pd.Timestamp("2024-05-20T00:00:00Z"),
        pd.Timestamp("2024-05-27T00:00:00Z"),
        pd.Timestamp("2024-06-03T00:00:00Z"),
        pd.Timestamp("2024-06-10T00:00:00Z"),
        pd.Timestamp("2024-06-17T00:00:00Z"),
    ]
    for date in tick_dates:
        x = _x_scale(date, left, width)
        parts.append(f'<line x1="{x:.2f}" y1="{top}" x2="{x:.2f}" y2="{top + height}" stroke="#f0f0f0" stroke-width="1"/>')
    parts.append(f'<line x1="{left}" y1="{top + height}" x2="{left + width}" y2="{top + height}" stroke="#333" stroke-width="2"/>')
    parts.append(f'<line x1="{left}" y1="{top}" x2="{left}" y2="{top + height}" stroke="#333" stroke-width="2"/>')
    parts.append(
        f'<text transform="translate({left - 70:.1f} {top + height / 2:.1f}) rotate(-90)" '
        'text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="24" fill="#333">'
        f'{html.escape(y_label)}</text>'
    )


def _band(parts: list[str], left: float, top: float, width: float, height: float, y_min: float, y_max: float, low: float, high: float, color: str) -> None:
    y1 = _y_scale(high, y_min, y_max, top, height)
    y2 = _y_scale(low, y_min, y_max, top, height)
    parts.append(f'<rect x="{left}" y="{y1:.2f}" width="{width}" height="{y2 - y1:.2f}" fill="{color}" fill-opacity="0.12"/>')
    parts.append(f'<line x1="{left}" y1="{y1:.2f}" x2="{left + width}" y2="{y1:.2f}" stroke="{color}" stroke-width="2" stroke-dasharray="7 5"/>')
    parts.append(f'<line x1="{left}" y1="{y2:.2f}" x2="{left + width}" y2="{y2:.2f}" stroke="{color}" stroke-width="2" stroke-dasharray="7 5"/>')


def write_svg(path: Path, grid: pd.DataFrame, protected: pd.DataFrame) -> None:
    width, height = 1650, 1130
    left, plot_width = 130, 1430
    top1, panel_h, gap = 220, 330, 68
    top2 = top1 + panel_h + gap
    green, red = "#4daf4a", "#ff6b6b"
    # CSR1 facility color, aligned with Figures 3, 5, and 6.
    grid_color, pv_color = "#333333", "#f28e2b"

    grid_points_v = _points(grid, "voltage", left, plot_width, top1, panel_h, -20, 330)
    pv_points_v = _points(protected, "voltage", left, plot_width, top1, panel_h, -20, 330)
    grid_points_f = _points(grid, "frequency", left, plot_width, top2, panel_h, 37, 63)
    pv_points_f = _points(protected, "frequency", left, plot_width, top2, panel_h, 37, 63)

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        '<style>text{font-family:Arial, Helvetica, sans-serif}</style>',
    ]

    _axis_panel(parts, "voltage", "Voltage (Vrms)", -20, 330, [0, 100, 200, 300], left, top1, plot_width, panel_h)
    _band(parts, left, top1, plot_width, panel_h, -20, 330, 207, 253, green)
    _band(parts, left, top1, plot_width, panel_h, -20, 330, -10, 40, red)
    x_int = _x_scale(INTERVENTION_DATE, left, plot_width)
    parts.append(f'<line x1="{x_int:.2f}" y1="{top1}" x2="{x_int:.2f}" y2="{top1 + panel_h}" stroke="#111" stroke-width="3" stroke-dasharray="9 6"/>')
    parts.extend(_circle_parts(grid_points_v, grid_color, 2.4, 0.72))
    parts.append(_polyline(pv_points_v, pv_color, 3.0, 0.65))
    parts.extend(_circle_parts(pv_points_v, pv_color, 4.0, 0.90))
    parts.append("</g>")

    _axis_panel(parts, "frequency", "Frequency (Hz)", 37, 63, [40, 45, 50, 55, 60], left, top2, plot_width, panel_h)
    _band(parts, left, top2, plot_width, panel_h, 37, 63, 49, 51, green)
    _band(parts, left, top2, plot_width, panel_h, 37, 63, 40, 41, red)
    parts.append(f'<line x1="{x_int:.2f}" y1="{top2}" x2="{x_int:.2f}" y2="{top2 + panel_h}" stroke="#111" stroke-width="3" stroke-dasharray="9 6"/>')
    parts.extend(_circle_parts(grid_points_f, grid_color, 2.3, 0.66))
    parts.append(_polyline(pv_points_f, pv_color, 3.0, 0.65))
    parts.extend(_circle_parts(pv_points_f, pv_color, 4.0, 0.90))
    parts.append("</g>")

    # Top annotations and arrows.
    pre_x1, pre_x2 = _x_scale(FIGURE_START, left, plot_width), _x_scale(pd.Timestamp("2024-05-15T12:00:00Z"), left, plot_width)
    post_x1, post_x2 = _x_scale(pd.Timestamp("2024-05-27T00:00:00Z"), left, plot_width), _x_scale(FIGURE_END, left, plot_width)
    arrow_y = 150
    parts.append(f'<text x="{(pre_x1 + pre_x2) / 2 - 45:.1f}" y="58" text-anchor="middle" font-size="22" font-weight="700" fill="#454545">Pre-intervention:</text>')
    parts.append(f'<text x="{(pre_x1 + pre_x2) / 2 - 45:.1f}" y="88" text-anchor="middle" font-size="22" font-weight="700" fill="#454545">micro-hydro grid only</text>')
    parts.append(f'<text x="{(pre_x1 + pre_x2) / 2 - 45:.1f}" y="124" text-anchor="middle" font-size="19" font-style="italic" fill="#777">Monitoring of existing micro-hydro system</text>')
    parts.append(f'<line x1="{pre_x1}" y1="{arrow_y}" x2="{pre_x2}" y2="{arrow_y}" stroke="#777" stroke-width="3"/>')
    parts.append(f'<polygon points="{pre_x1},{arrow_y} {pre_x1 + 11},{arrow_y - 7} {pre_x1 + 11},{arrow_y + 7}" fill="#777"/>')
    parts.append(f'<polygon points="{pre_x2},{arrow_y} {pre_x2 - 11},{arrow_y - 7} {pre_x2 - 11},{arrow_y + 7}" fill="#777"/>')
    parts.append(f'<text x="{x_int:.1f}" y="32" text-anchor="middle" font-size="23" font-weight="700" fill="#222">Intervention date</text>')
    parts.append(f'<text x="{x_int:.1f}" y="62" text-anchor="middle" font-size="23" font-weight="700" fill="#222">(May 16, 2024)</text>')
    parts.append(f'<text x="{(post_x1 + post_x2) / 2:.1f}" y="75" text-anchor="middle" font-size="23" font-weight="700" fill="{pv_color}">Post-intervention: stacked system</text>')
    parts.append(f'<text x="{(post_x1 + post_x2) / 2:.1f}" y="105" text-anchor="middle" font-size="18" font-style="italic" font-weight="700" fill="{pv_color}">Protected PV circuit in use for critical loads;</text>')
    parts.append(f'<text x="{(post_x1 + post_x2) / 2:.1f}" y="128" text-anchor="middle" font-size="18" font-style="italic" font-weight="700" fill="{pv_color}">micro-hydro remains available for other uses</text>')
    parts.append(f'<line x1="{post_x1}" y1="{arrow_y}" x2="{post_x2}" y2="{arrow_y}" stroke="{pv_color}" stroke-width="3"/>')
    parts.append(f'<polygon points="{post_x1},{arrow_y} {post_x1 + 11},{arrow_y - 7} {post_x1 + 11},{arrow_y + 7}" fill="{pv_color}"/>')
    parts.append(f'<polygon points="{post_x2},{arrow_y} {post_x2 - 11},{arrow_y - 7} {post_x2 - 11},{arrow_y + 7}" fill="{pv_color}"/>')

    # Bottom date axis labels.
    tick_dates = [
        pd.Timestamp("2024-04-29T00:00:00Z"),
        pd.Timestamp("2024-05-06T00:00:00Z"),
        pd.Timestamp("2024-05-13T00:00:00Z"),
        pd.Timestamp("2024-05-20T00:00:00Z"),
        pd.Timestamp("2024-05-27T00:00:00Z"),
        pd.Timestamp("2024-06-03T00:00:00Z"),
        pd.Timestamp("2024-06-10T00:00:00Z"),
        pd.Timestamp("2024-06-17T00:00:00Z"),
    ]
    axis_y = top2 + panel_h
    for date in tick_dates:
        x = _x_scale(date, left, plot_width)
        label = f"{date.month}/{date.day}"
        parts.append(f'<line x1="{x:.2f}" y1="{axis_y}" x2="{x:.2f}" y2="{axis_y + 9}" stroke="#333" stroke-width="1.6"/>')
        parts.append(f'<text x="{x:.2f}" y="{axis_y + 35}" text-anchor="middle" font-size="19" fill="#333">{label}</text>')
    parts.append(f'<text x="{left + plot_width / 2:.1f}" y="{axis_y + 70}" text-anchor="middle" font-size="24" fill="#333">Date</text>')

    # Legend.
    legend_y = height - 52
    legend_x = 270
    parts.append(f'<circle cx="{legend_x}" cy="{legend_y}" r="5" fill="{grid_color}" fill-opacity="0.85"/>')
    parts.append(f'<text x="{legend_x + 35}" y="{legend_y + 7}" font-size="19" fill="#333">Existing micro-hydro grid (pre- and post-intervention)</text>')
    legend_x2 = 800
    parts.append(f'<line x1="{legend_x2}" y1="{legend_y}" x2="{legend_x2 + 35}" y2="{legend_y}" stroke="{pv_color}" stroke-width="3"/>')
    parts.append(f'<circle cx="{legend_x2 + 18}" cy="{legend_y}" r="5" fill="{pv_color}"/>')
    parts.append(f'<text x="{legend_x2 + 50}" y="{legend_y + 7}" font-size="19" fill="#333">Protected PV circuit (post-intervention, CSR1)</text>')

    parts.append("</svg>")
    path.write_text("\n".join(parts), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw-root", type=Path, default=DEFAULT_RAW_ROOT)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    args = parser.parse_args()

    grid = _display_sample(_load_powerwatch(args.raw_root, "CSR1-PW-02"), keep_outages=True)
    protected = _display_sample(_load_powerwatch(args.raw_root, "CSR1-PW-03"), keep_outages=False)

    output = args.output_root / "figure3"
    output.mkdir(parents=True, exist_ok=True)
    grid.assign(series="existing_micro_hydro").to_csv(output / "csr1_existing_micro_hydro_timeseries_sample.csv", index=False)
    protected.assign(series="protected_pv_circuit").to_csv(output / "csr1_protected_pv_timeseries_sample.csv", index=False)
    write_svg(output / "csr1_pre_post_timeseries.svg", grid, protected)
    print(f"figure 3 top panel: {len(grid)} existing-grid points; {len(protected)} protected-circuit points")


if __name__ == "__main__":
    main()
