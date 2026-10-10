"""Assemble Figure 3 with explicit reconstructed and inherited provenance."""

import pandas as pd


SHORT_SOURCE_WINDOWS = {"CH1": "ch1_inherited_source", "CSR2": "csr2_inherited_source",
                        "CSR4": "csr4_inherited_source"}


def reconstructed_comparisons(inherited: pd.DataFrame, audit: pd.DataFrame,
                              policy: str = "joint") -> pd.DataFrame:
    if policy not in ("joint", "independent"):
        raise ValueError("PQR policy must be joint or independent")
    data = inherited.set_index("facility_code").copy()
    data["baseline_sensor_basis"] = "inherited_not_independently_reconstructed"
    data["baseline_comparison_type"] = "inherited_baseline"
    for facility, window_id in SHORT_SOURCE_WINDOWS.items():
        selected = audit[audit.window_id == window_id]
        if len(selected) != 1 or selected.iloc[0].expected_intervals == 0:
            raise ValueError(f"Missing unique reconstructed source window: {window_id}")
        row = selected.iloc[0]
        data.loc[facility, "uptime_pct"] = row.expected_window_uptime_pct
        data.loc[facility, "voltage_quality_pct"] = row[
            "legacy_joint_voltage_quality_pct" if policy == "joint" else "voltage_quality_pct"]
        for tolerance in ("1", "5", "10"):
            data.loc[facility, f"frequency_quality_{tolerance}_pct"] = row[f"frequency_quality_{tolerance}_pct"]
        data.loc[facility, "status"] = "reconstructed_existing_source_comparison"
        data.loc[facility, "baseline_sensor_basis"] = "single_powerwatch"
        data.loc[facility, "baseline_comparison_type"] = "existing_source_not_preinstallation"
        data.loc[facility, "baseline_sensor_id"] = row.sensor_id
        data.loc[facility, "baseline_window_start"] = row.first_valid
        data.loc[facility, "baseline_window_end"] = row.last_valid
        data.loc[facility, "baseline_observed_uptime_pct"] = row.observed_uptime_pct
        data.loc[facility, "baseline_coverage_pct"] = row.coverage_pct
        data.loc[facility, "baseline_source_status"] = row.source_status
    data["pqr_denominator_policy"] = policy
    return data.reset_index()
