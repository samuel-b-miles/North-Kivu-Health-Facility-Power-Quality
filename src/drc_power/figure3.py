"""Assemble Figure 3 with explicit reconstructed and inherited provenance."""

import pandas as pd


SHORT_SOURCE_WINDOWS = {"CH1": "ch1_inherited_source", "CSR2": "csr2_inherited_source",
                        "CSR4": "csr4_inherited_source"}


def reconstructed_comparisons(inherited: pd.DataFrame, audit: pd.DataFrame,
                              policy: str = "joint", longitudinal: pd.DataFrame | None = None) -> pd.DataFrame:
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
        for tolerance in ("0_1", "1", "5", "10"):
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
    if longitudinal is not None:
        for facility in ("HGR1", "CSR1", "CSR3"):
            if facility not in data.index:
                continue
            chosen = longitudinal[longitudinal.facility_code == facility]
            if len(chosen) != 1 or chosen.iloc[0].expected_intervals <= 0:
                raise ValueError(f"Missing unique reconstructed longitudinal baseline: {facility}")
            row = chosen.iloc[0]
            data.loc[facility, "uptime_pct"] = row.expected_window_uptime_pct
            data.loc[facility, "voltage_quality_pct"] = row[
                "legacy_joint_voltage_quality_pct" if policy == "joint" else "voltage_quality_pct"]
            # The saved ±0.1% value uses the same joint-valid frequency readings
            # and equal sensor means; older audits have no legacy alias for it.
            for tolerance in ("0_1", "1", "5", "10"):
                key = f"legacy_joint_frequency_{tolerance}_pct" if policy == "joint" and tolerance != "0_1" else f"frequency_quality_{tolerance}_pct"
                data.loc[facility, f"frequency_quality_{tolerance}_pct"] = row[key]
            data.loc[facility, "status"] = "reconstructed_longitudinal_pre_source_window"
            data.loc[facility, "baseline_sensor_basis"] = "two_powerwatch_variable_coverage"
            data.loc[facility, "baseline_comparison_type"] = "pre_intervention_source_monitoring"
            data.loc[facility, "baseline_sensor_id"] = row.sensor_ids
            data.loc[facility, "baseline_window_start"] = row.window_start
            data.loc[facility, "baseline_window_end"] = row.window_end_inclusive
            data.loc[facility, "baseline_observed_uptime_pct"] = row.observed_uptime_pct
            data.loc[facility, "baseline_coverage_pct"] = row.coverage_pct
            data.loc[facility, "baseline_two_sensor_coverage_pct"] = row.two_sensor_coverage_pct
            data.loc[facility, "baseline_source_status"] = "verified_device_crosswalk; cutoff_is_configured_source_start"
            data.loc[facility, "baseline_window_basis"] = row.window_basis
            data.loc[facility, "baseline_selection_rationale"] = row.selection_rationale
            data.loc[facility, "baseline_quality_aggregation"] = row.quality_aggregation
    data["pqr_denominator_policy"] = policy
    return data.reset_index()
