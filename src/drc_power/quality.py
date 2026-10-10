"""Conditional voltage and frequency quality estimands."""

from __future__ import annotations

import pandas as pd


def _percent(mask: pd.Series) -> float:
    return float(mask.mean() * 100) if len(mask) else float("nan")


def conditional_power_quality(
    frame: pd.DataFrame,
    *,
    outage_voltage: float = 23.0,
    voltage_min: float = 207.0,
    voltage_max: float = 253.0,
    voltage_physical_max: float = 400.0,
    frequency_nominal: float = 50.0,
    frequency_physical_min: float = 30.0,
    frequency_physical_max: float = 70.0,
) -> dict[str, float | int]:
    """Calculate quality conditional on observed usable power.

    Voltage and frequency denominators are kept separate so an invalid frequency
    reading cannot silently remove an otherwise valid voltage observation.
    """
    voltage = pd.to_numeric(frame["voltage"], errors="coerce")
    powered_voltage = voltage[(voltage >= outage_voltage) & (voltage <= voltage_physical_max)]
    result: dict[str, float | int] = {
        "observations": int(len(frame)),
        "powered_voltage_observations": int(len(powered_voltage)),
        "outage_voltage_observations": int((voltage < outage_voltage).sum()),
        "invalid_voltage_observations": int((voltage > voltage_physical_max).sum()),
        "voltage_quality_pct": _percent(
            (powered_voltage >= voltage_min) & (powered_voltage <= voltage_max)
        ),
    }
    if "frequency" not in frame:
        return result
    frequency = pd.to_numeric(frame.loc[powered_voltage.index, "frequency"], errors="coerce")
    valid_frequency = frequency[
        (frequency >= frequency_physical_min) & (frequency <= frequency_physical_max)
    ]
    result["valid_frequency_observations"] = int(len(valid_frequency))
    result["invalid_frequency_observations"] = int(
        ((frequency < frequency_physical_min) | (frequency > frequency_physical_max)).sum()
    )
    for label, tolerance in (("0_1", 0.001), ("1", 0.01), ("5", 0.05), ("10", 0.10)):
        lower = frequency_nominal * (1 - tolerance)
        upper = frequency_nominal * (1 + tolerance)
        result[f"frequency_quality_{label}_pct"] = _percent(
            (valid_frequency >= lower) & (valid_frequency <= upper)
        )
    return result


def joint_valid_power_quality(frame: pd.DataFrame) -> dict[str, float | int]:
    """Reproduce the inherited complete-case voltage/frequency estimand.

    Unlike the default independent denominators, voltage is assessed only where
    frequency is also physically valid. Keep both policies available explicitly.
    """
    voltage = pd.to_numeric(frame["voltage"], errors="coerce")
    frequency = pd.to_numeric(frame["frequency"], errors="coerce")
    retained = frame[voltage.between(23, 400) & frequency.between(30, 70)]
    return {**conditional_power_quality(retained), "input_observations": len(frame),
            "joint_valid_observations": len(retained)}
