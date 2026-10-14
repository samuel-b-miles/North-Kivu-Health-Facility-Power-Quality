import pandas as pd
import pytest

from drc_power.figure3 import reconstructed_comparisons
from drc_power.quality import joint_valid_power_quality


def inputs():
    inherited = pd.DataFrame([{"facility_code": f, "uptime_pct": 90., "voltage_quality_pct": 80.,
                              "frequency_quality_5_pct": 70., "status": "inherited"}
                             for f in ["CH1", "CSR2", "CSR4", "HGR1"]])
    rows = []
    for f, key in [("CH1", "ch1"), ("CSR2", "csr2"), ("CSR4", "csr4")]:
        rows.append({"window_id": key + "_inherited_source", "expected_intervals": 10,
                     "expected_window_uptime_pct": 50., "observed_uptime_pct": 75.,
                     "legacy_joint_voltage_quality_pct": 20., "voltage_quality_pct": 40.,
                     "frequency_quality_0_1_pct": 2., "frequency_quality_1_pct": 10., "frequency_quality_5_pct": 30.,
                     "frequency_quality_10_pct": 60., "sensor_id": f + "-PW-01",
                     "first_valid": "2024-01-01", "last_valid": "2024-01-02",
                     "coverage_pct": 80., "source_status": "source_history_unconfirmed"})
    return inherited, pd.DataFrame(rows)


def test_reconstructed_values_replace_only_supported_facilities():
    inherited, audit = inputs()
    result = reconstructed_comparisons(inherited, audit).set_index("facility_code")
    assert result.loc["CH1", "frequency_quality_0_1_pct"] == 2
    assert result.loc["CH1", "uptime_pct"] == 50
    assert result.loc["CH1", "voltage_quality_pct"] == 20
    assert result.loc["HGR1", "uptime_pct"] == 90
    assert pd.isna(result.loc["HGR1", "frequency_quality_1_pct"])
    assert result.loc["CH1", "baseline_comparison_type"] == "existing_source_not_preinstallation"


def test_independent_pqr_sensitivity_is_explicit():
    inherited, audit = inputs()
    result = reconstructed_comparisons(inherited, audit, "independent")
    assert result.iloc[0].voltage_quality_pct == 40
    assert (result.pqr_denominator_policy == "independent").all()


def test_missing_audit_does_not_silently_fall_back_to_inherited_values():
    inherited, audit = inputs()
    with pytest.raises(ValueError, match="Missing unique"):
        reconstructed_comparisons(inherited, audit.iloc[1:])


def test_joint_valid_policy_exposes_frequency_selection():
    frame = pd.DataFrame({"voltage": [230, 260, 230, 0], "frequency": [50, None, 1000, 50]})
    result = joint_valid_power_quality(frame)
    assert result["input_observations"] == 4
    assert result["joint_valid_observations"] == 1
    assert result["voltage_quality_pct"] == 100


def test_longitudinal_baseline_replaces_inherited_and_retains_coverage():
    inherited, audit = inputs()
    longitudinal = pd.DataFrame([{
        "facility_code": "HGR1", "expected_intervals": 100,
        "expected_window_uptime_pct": 99., "observed_uptime_pct": 99.5,
        "coverage_pct": 99.8, "two_sensor_coverage_pct": 85.,
        "legacy_joint_voltage_quality_pct": 98., "voltage_quality_pct": 97.,
        "frequency_quality_0_1_pct": 3., "legacy_joint_frequency_1_pct": 34., "legacy_joint_frequency_5_pct": 94.,
        "legacy_joint_frequency_10_pct": 99., "frequency_quality_1_pct": 35.,
        "frequency_quality_5_pct": 95., "frequency_quality_10_pct": 99.5,
        "sensor_ids": "HGR1-PW-01;HGR1-PW-02", "window_start": "2022-01-01",
        "window_end_inclusive": "2024-01-01", "window_basis": "shared_overlap",
        "selection_rationale": "shared pre-source window", "quality_aggregation": "equal_sensor_mean"}])
    result = reconstructed_comparisons(inherited, audit, longitudinal=longitudinal).set_index("facility_code")
    assert result.loc["HGR1", "frequency_quality_0_1_pct"] == 3
    assert result.loc["HGR1", "uptime_pct"] == 99
    assert result.loc["HGR1", "frequency_quality_1_pct"] == 34
    assert result.loc["HGR1", "baseline_two_sensor_coverage_pct"] == 85
    assert result.loc["HGR1", "baseline_sensor_basis"] == "two_powerwatch_variable_coverage"
    independent = reconstructed_comparisons(inherited, audit, "independent", longitudinal).set_index("facility_code")
    assert independent.loc["HGR1", "frequency_quality_5_pct"] == 95
    with pytest.raises(ValueError, match="longitudinal baseline"):
        reconstructed_comparisons(inherited, audit, longitudinal=longitudinal.iloc[:0])
