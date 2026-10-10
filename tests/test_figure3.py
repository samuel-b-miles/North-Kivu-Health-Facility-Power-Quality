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
                     "frequency_quality_1_pct": 10., "frequency_quality_5_pct": 30.,
                     "frequency_quality_10_pct": 60., "sensor_id": f + "-PW-01",
                     "first_valid": "2024-01-01", "last_valid": "2024-01-02",
                     "coverage_pct": 80., "source_status": "source_history_unconfirmed"})
    return inherited, pd.DataFrame(rows)


def test_reconstructed_values_replace_only_supported_facilities():
    inherited, audit = inputs()
    result = reconstructed_comparisons(inherited, audit).set_index("facility_code")
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
