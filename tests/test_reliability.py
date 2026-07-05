import pandas as pd

from drc_power.reliability import paired_reliability, single_sensor_reliability


def _frame(values):
    return pd.DataFrame(
        {
            "time": pd.date_range("2025-01-01", periods=len(values), freq="2min", tz="UTC"),
            "voltage": values,
        }
    )


def test_single_sensor_keeps_missing_as_unknown():
    result = single_sensor_reliability(_frame([230, None, 0]))
    assert result["powered_intervals"] == 1
    assert result["observed_outage_intervals"] == 1
    assert result["unknown_intervals"] == 1
    assert result["observed_availability_pct"] == 50.0


def test_paired_outage_requires_both_sensors():
    hop = _frame([230, 0, 0, None])
    pw = _frame([230, 0, 230, 0])
    result = paired_reliability(hop, pw)
    assert result["confirmed_powered_intervals"] == 1
    assert result["confirmed_outage_intervals"] == 1
    assert result["discordant_intervals"] == 1
    assert result["unknown_intervals"] == 1
    assert result["availability_among_assessed_concordant_intervals_pct"] == 50.0
