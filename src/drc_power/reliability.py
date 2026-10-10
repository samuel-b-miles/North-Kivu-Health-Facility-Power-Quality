"""Reliability estimands that preserve missing telemetry as unknown."""

from __future__ import annotations

import pandas as pd
from drc_power.monitoring_audit import monitoring_summary


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
    exclusions: tuple | list[tuple[pd.Timestamp, pd.Timestamp | None]] = (),
) -> dict[str, float | int]:
    hop_v = _binned_voltage(hop, interval).rename("hop")
    pw_v = _binned_voltage(powerwatch, interval).rename("powerwatch")
    aligned = pd.concat([hop_v, pw_v], axis=1)
    for start, end in exclusions:
        aligned = aligned[~((aligned.index >= start) & ((aligned.index < end) if end is not None else True))]
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
        "availability_among_assessed_concordant_intervals_pct": float(confirmed_powered.sum() / assessed.sum() * 100) if assessed.sum() else float("nan"),
    }


def manuscript_at_least_one_sensor_uptime(
    hop: pd.DataFrame,
    powerwatch: pd.DataFrame,
    *,
    interval: str = "2min",
    outage_voltage: float = 23.0,
    exclusions: tuple | list[tuple[pd.Timestamp, pd.Timestamp | None]] = (),
) -> dict[str, float | int | str]:
    """Implement and decompose the manuscript's at-least-one-sensor rule.

    The shared monitoring window begins at the later first valid observation and
    ends at the earlier last valid observation. We expose both a conservative
    expected-window denominator and an observed-evidence denominator because the
    manuscript wording does not yet specify how intervals with no telemetry from
    either sensor enter the denominator.
    """
    summary = monitoring_summary({"hop": hop, "powerwatch": powerwatch},
                                 interval=interval, outage_voltage=outage_voltage,
                                 exclusions=exclusions)
    return {
        **summary,
        "shared_window_start": summary.get("window_start", ""),
        "shared_window_end": summary.get("window_end_inclusive", ""),
        "any_sensor_observed_intervals": summary.get("observed_intervals", 0),
        "any_sensor_powered_intervals": summary.get("powered_intervals", 0),
        "both_sensors_missing_intervals": summary.get("unknown_intervals", 0),
        "manuscript_uptime_expected_window_pct": summary["expected_window_uptime_pct"],
        "manuscript_uptime_observed_evidence_pct": summary["observed_uptime_pct"],
    }
