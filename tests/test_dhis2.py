import pandas as pd

from drc_power.dhis2 import (
    audit_duplicate_columns,
    build_facility_month,
    longest_streak,
    table2_metrics,
)


def test_duplicate_audit_detects_nonoverlapping_exports():
    frame = pd.DataFrame({"indicator": [1, None], "indicator.1": [None, 2]})
    audit = audit_duplicate_columns(frame, "test").iloc[0]
    assert audit["base_only_n"] == 1
    assert audit["duplicate_only_n"] == 1
    assert audit["conflict_n"] == 0


def test_longest_reporting_streak():
    assert longest_streak(pd.Series([True, True, False, True, True, True])) == 3


def test_facility_month_uses_only_reported_admission_wards():
    ward = pd.DataFrame({
        "facility_id_anonymized": ["FAC_T01", "FAC_T01"],
        "display_code": ["HGR1", "HGR1"], "arm": ["treatment", "treatment"],
        "facility_type": ["HGR", "HGR"], "month": ["2023-01", "2023-01"],
        "admissions_reported": [True, False], "admissions": [10.0, None],
        "deaths_total": [1.0, 5.0],
    })
    result = build_facility_month(ward).iloc[0]
    assert result["admissions"] == 10
    assert result["deaths_total"] == 1
    assert result["mortality_rate"] == 0.1


def test_table2_denominators_are_arm_specific():
    facility = pd.DataFrame({
        "arm": ["treatment", "treatment", "control", "control"],
        "facility_id_anonymized": ["FAC_T01", "FAC_T01", "FAC_C01", "FAC_C01"],
        "facility_month_reported": [True, False, True, True],
        "deaths_total": [1, 0, 0, 1], "admissions": [10, None, 20, 20],
        "mortality_rate": [0.1, None, 0, 0.05],
    })
    ward = pd.DataFrame({"arm": ["treatment", "treatment", "control", "control"], "admissions_reported": [True, False, True, True]})
    result = table2_metrics(ward, facility).set_index("arm")
    assert result.loc["treatment", "facility_month_reporting_completeness_pct"] == 50
    assert result.loc["control", "facility_months_with_deaths_pct"] == 50
