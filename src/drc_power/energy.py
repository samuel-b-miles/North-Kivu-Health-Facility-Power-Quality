"""Daily-energy parsing and aggregation with explicit missingness."""

from __future__ import annotations

import re

import pandas as pd


def parse_energy_wh(value: object) -> float:
    text = str(value).strip()
    match = re.fullmatch(r"([-+]?\d*\.?\d+)\s*(kWh|Wh)?", text, flags=re.IGNORECASE)
    if not match:
        return float("nan")
    amount = float(match.group(1))
    unit = (match.group(2) or "Wh").lower()
    return amount * 1000 if unit == "kwh" else amount


def aggregate_daily_energy(sensor_frames: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Aggregate distinct downstream meters without converting missing days to zero."""
    series = []
    for sensor_id, frame in sensor_frames.items():
        data = frame[["Time", "Energy per Day"]].copy()
        data["date"] = pd.to_datetime(data["Time"], errors="coerce", utc=True).dt.date
        data[sensor_id] = data["Energy per Day"].map(parse_energy_wh) / 1000
        series.append(data.dropna(subset=["date"]).set_index("date")[sensor_id])
    combined = pd.concat(series, axis=1).sort_index()
    combined["facility_total_kwh"] = combined.sum(axis=1, min_count=1)
    combined["reporting_sensors"] = combined.notna().sum(axis=1) - 1
    return combined

