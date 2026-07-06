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
