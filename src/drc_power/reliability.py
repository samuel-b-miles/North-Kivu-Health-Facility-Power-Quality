"""Reliability estimands that preserve missing telemetry as unknown."""

from __future__ import annotations

import pandas as pd


def _binned_voltage(frame: pd.DataFrame, interval: str) -> pd.Series:
    data = frame[["time", "voltage"]].copy()
    data["time"] = pd.to_datetime(data["time"], errors="coerce", utc=True)
    data["voltage"] = pd.to_numeric(data["voltage"], errors="coerce")
    data = data.dropna(subset=["time"]).set_index("time").sort_index()
    return data["voltage"].resample(interval).median()


def single_sensor_reliability(
    frame: pd.DataFrame, *, interval: str = "2min", outage_voltage: float = 23.0
) -> dict[str, float | int]:
    voltage = _binned_voltage(frame, interval)
    observed = voltage.notna()
    powered = observed & (voltage > outage_voltage)
    outage = observed & (voltage <= outage_voltage)
    total = len(voltage)
    return {
        "expected_intervals": total,
        "powered_intervals": int(powered.sum()),
        "observed_outage_intervals": int(outage.sum()),
        "unknown_intervals": int((~observed).sum()),
        "observed_availability_pct": float(powered.sum() / observed.sum() * 100) if observed.sum() else float("nan"),
        "conservative_availability_pct": float(powered.sum() / total * 100) if total else float("nan"),
    }


def paired_reliability(
    hop: pd.DataFrame,
    powerwatch: pd.DataFrame,
    *,
    interval: str = "2min",
    outage_voltage: float = 23.0,
) -> dict[str, float | int]:
    hop_v = _binned_voltage(hop, interval).rename("hop")
    pw_v = _binned_voltage(powerwatch, interval).rename("powerwatch")
    aligned = pd.concat([hop_v, pw_v], axis=1)
    both_observed = aligned.notna().all(axis=1)
    confirmed_outage = both_observed & (aligned["hop"] <= outage_voltage) & (aligned["powerwatch"] <= outage_voltage)
    confirmed_powered = both_observed & (aligned["hop"] > outage_voltage) & (aligned["powerwatch"] > outage_voltage)
    discordant = both_observed & ~(confirmed_outage | confirmed_powered)
    assessed = confirmed_outage | confirmed_powered
    return {
        "aligned_intervals": len(aligned),
        "both_observed_intervals": int(both_observed.sum()),
        "confirmed_powered_intervals": int(confirmed_powered.sum()),
        "confirmed_outage_intervals": int(confirmed_outage.sum()),
        "discordant_intervals": int(discordant.sum()),
        "unknown_intervals": int((~both_observed).sum()),
        "confirmed_availability_pct": float(confirmed_powered.sum() / assessed.sum() * 100) if assessed.sum() else float("nan"),
    }

