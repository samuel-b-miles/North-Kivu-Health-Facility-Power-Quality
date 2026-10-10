"""Explicit monitoring denominators for single and paired sensor audits."""

from __future__ import annotations

import pandas as pd


def monitoring_summary(
    frames: dict[str, pd.DataFrame],
    *,
    start: pd.Timestamp | None = None,
    end: pd.Timestamp | None = None,
    exclusions: tuple | list[tuple[pd.Timestamp, pd.Timestamp | None]] = (),
    interval: str = "2min",
    outage_voltage: float = 23.0,
) -> dict:
    """Use two-minute medians; end is exclusive; missingness stays explicit.

    Without explicit bounds, use the overlap of first/last valid readings.
    Two inputs are appropriate only when their circuit/source identity matches.
    """
    if len(frames) not in (1, 2):
        raise ValueError("Supply one sensor or two confirmed co-source sensors")
    series = {}
    for name, frame in frames.items():
        data = frame[["time", "voltage"]].dropna(subset=["time"]).copy()
        data["time"] = pd.to_datetime(data["time"], utc=True)
        data["voltage"] = pd.to_numeric(data["voltage"], errors="coerce")
        if start is not None:
            data = data[data.time >= start]
        if end is not None:
            data = data[data.time < end]
        series[name] = data.set_index("time").voltage.sort_index().resample(interval).median()
    valid = [s.dropna() for s in series.values()]
    if any(s.empty for s in valid) and (start is None or end is None):
        return {"sensor_count": len(frames), "expected_intervals": 0,
                "observed_uptime_pct": float("nan"), "expected_window_uptime_pct": float("nan"),
                "status": "no_valid_voltage"}
    first = start.floor(interval) if start is not None else max(s.index.min() for s in valid)
    last = end.ceil(interval) - pd.Timedelta(interval) if end is not None else min(s.index.max() for s in valid)
    if first > last:
        return {"sensor_count": len(frames), "expected_intervals": 0,
                "observed_uptime_pct": float("nan"), "expected_window_uptime_pct": float("nan"),
                "status": "no_shared_window"}
    index = pd.date_range(first, last, freq=interval)
    for a, b in exclusions:
        index = index[~((index >= a) & ((index < b) if b is not None else True))]
    aligned = pd.DataFrame({name: s.reindex(index) for name, s in series.items()})
    n_observed = aligned.notna().sum(axis=1)
    powered = (aligned > outage_voltage).any(axis=1)
    observed = n_observed > 0
    both = n_observed == 2
    both_low = both & (aligned <= outage_voltage).all(axis=1)
    discordant = both & (aligned > outage_voltage).any(axis=1) & (aligned <= outage_voltage).any(axis=1)
    count = len(index)
    percent = lambda n, d: float(n / d * 100) if d else float("nan")
    return {
        "sensor_count": len(frames), "window_start": first.isoformat(),
        "window_end_inclusive": last.isoformat(), "expected_intervals": count,
        "observed_intervals": int(observed.sum()), "powered_intervals": int(powered.sum()),
        "unknown_intervals": int((~observed).sum()),
        "one_sensor_observed_intervals": int((n_observed == 1).sum()),
        "two_sensors_observed_intervals": int(both.sum()),
        "two_sensors_low_intervals": int(both_low.sum()),
        "discordant_intervals": int(discordant.sum()),
        "single_sensor_low_intervals": int(((n_observed == 1) & ~powered).sum()),
        "observed_uptime_pct": percent(powered.sum(), observed.sum()),
        "expected_window_uptime_pct": percent(powered.sum(), count),
        "coverage_pct": percent(observed.sum(), count),
        "two_sensor_coverage_pct": percent(both.sum(), count) if len(frames) == 2 else float("nan"),
        "status": "calculated_source_interpretation_requires_review",
    }
