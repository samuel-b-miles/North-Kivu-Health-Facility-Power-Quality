import pandas as pd

from drc_power.reliability import manuscript_at_least_one_sensor_uptime, paired_reliability, single_sensor_reliability


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


def test_manuscript_uptime_reports_both_denominators():
    hop = _frame([230, None, 0, None])
    pw = _frame([None, 230, 0, None])
    result = manuscript_at_least_one_sensor_uptime(hop, pw)
    # The shared valid-data window begins at PW's first valid interval and ends
    # at the third interval, before trailing missingness.
    assert result["expected_intervals"] == 2
    assert result["any_sensor_powered_intervals"] == 1
    assert result["manuscript_uptime_expected_window_pct"] == 50.0
    assert result["manuscript_uptime_observed_evidence_pct"] == 50.0


def test_excluded_period_is_not_reinserted_as_missing_by_resampling():
    hop = _frame([230, None, None, 230])
    pw = _frame([230, None, None, 230])
    exclusions = [(hop.time.iloc[1], hop.time.iloc[3])]
    result = manuscript_at_least_one_sensor_uptime(hop, pw, exclusions=exclusions)
    assert result["expected_intervals"] == 2
    assert result["both_sensors_missing_intervals"] == 0
    assert result["manuscript_uptime_expected_window_pct"] == 100
    diagnostic = paired_reliability(hop, pw, exclusions=exclusions)
    assert diagnostic["aligned_intervals"] == 2
