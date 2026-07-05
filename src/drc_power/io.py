"""Schema-normalizing readers for approved release assets."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


def read_powerwatch(path: str | Path) -> pd.DataFrame:
    frame = pd.read_csv(path, low_memory=False)
    frame.columns = frame.columns.str.lower()
    required = {"time", "voltage", "frequency"}
    missing = required - set(frame.columns)
    if missing:
        raise ValueError(f"PowerWatch file missing columns: {sorted(missing)}")
    result = frame[["time", "voltage", "frequency"]].copy()
    result["time"] = pd.to_datetime(result["time"], errors="coerce", utc=True)
    result["voltage"] = pd.to_numeric(result["voltage"], errors="coerce")
    result["frequency"] = pd.to_numeric(result["frequency"], errors="coerce")
    return result.dropna(subset=["time"]).sort_values("time")


def read_hop_voltage(path: str | Path) -> pd.DataFrame:
    frame = pd.read_csv(path, usecols=["time", "total"], low_memory=False)
    frame["time"] = pd.to_datetime(frame["time"], errors="coerce", utc=True)
    frame["voltage"] = pd.to_numeric(
        frame["total"].astype("string").str.replace(" V", "", regex=False),
        errors="coerce",
    )
    return frame[["time", "voltage"]].dropna(subset=["time"]).sort_values("time")

