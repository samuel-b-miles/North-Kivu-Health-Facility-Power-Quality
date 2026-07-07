"""Build annex-ready tables from generated analysis outputs."""

from __future__ import annotations

from pathlib import Path
import pandas as pd


FACILITY_ORDER = ["HGR1", "CH1", "CSR1", "CSR2", "CSR3", "CSR4"]


def _ordered(frame: pd.DataFrame, column: str = "facility_code") -> pd.DataFrame:
    result = frame.copy()
    result["_order"] = result[column].map({code: i for i, code in enumerate(FACILITY_ORDER)})
    return result.sort_values("_order").drop(columns="_order").reset_index(drop=True)


def build_power_quality_table(summary: pd.DataFrame, reliability: pd.DataFrame) -> pd.DataFrame:
    columns = [
        "facility_code", "uptime_pre_pct", "uptime_post_pct", "voltage_pre_pct",
        "voltage_post_pct", "frequency_5_pre_pct", "frequency_5_post_pct", "pre_status",
    ]
    windows = reliability[reliability["primary_facility_result"]].copy()
    windows = windows[["facility_code", "shared_window_start", "shared_window_end"]]
    result = summary[columns].merge(windows, on="facility_code", how="left")
    for column in columns[1:7]:
        result[column] = result[column].round(1)
    result["post_status"] = "repository_reproduced_provisional"
    return _ordered(result)


def build_energy_table(totals: pd.DataFrame, energy_by_meter: pd.DataFrame) -> pd.DataFrame:
    grouped = energy_by_meter.groupby("facility_code", as_index=False).agg(
        monitoring_days=("reporting_days", "max"),
        first_reporting_date=("first_reporting_date", "min") if "first_reporting_date" in energy_by_meter else ("reporting_days", lambda _: "see source"),
        last_reporting_date=("last_reporting_date", "max") if "last_reporting_date" in energy_by_meter else ("reporting_days", lambda _: "see source"),
    )
    result = totals.merge(grouped, on="facility_code", how="left")
    result["daily_mean_kwh"] = result["total_installed_system_consumption_kwh"] / result["monitoring_days"]
    result = result[[
        "facility_code", "total_installed_system_consumption_kwh", "critical_core_consumption_kwh",
        "supplemental_morgue_consumption_kwh", "included_meters", "monitoring_days", "daily_mean_kwh", "status",
    ]]
    for column in ["total_installed_system_consumption_kwh", "critical_core_consumption_kwh", "supplemental_morgue_consumption_kwh"]:
        result[column] = result[column].round(2)
    result["daily_mean_kwh"] = result["daily_mean_kwh"].round(2)
    return _ordered(result)


def build_health_facility_table(completeness: pd.DataFrame) -> pd.DataFrame:
    result = completeness.copy()
    result["reporting_completeness_pct"] = (100 * result["months_reported"] / 36).round(1)
    result["mean_monthly_admissions"] = result["mean_monthly_admissions"].round(1)
    result["mean_mortality_rate_pct"] = (100 * result["mean_mortality_rate"]).round(2)
    return result[[
        "facility_id_anonymized", "display_code", "arm", "months_reported",
        "reporting_completeness_pct", "longest_reporting_streak_months",
        "mean_monthly_admissions", "mean_mortality_rate_pct",
    ]].sort_values(["arm", "display_code"]).reset_index(drop=True)


def build_payment_table(facility: pd.DataFrame) -> pd.DataFrame:
    result = facility.copy()
    result["received_usd"] = result["received_usd"].round(2)
    result["on_time_pct"] = result["on_time_pct"].round(1)
    return _ordered(result)


def build_annex_tables(generated_root: Path, config_root: Path, output_root: Path) -> dict[str, Path]:
    output_root.mkdir(parents=True, exist_ok=True)
    figure3 = pd.read_csv(generated_root / "figure3" / "pre_post_summary.csv")
    reliability = pd.read_csv(generated_root / "reliability" / "manuscript_uptime_sensitivity.csv")
    totals = pd.read_csv(generated_root / "energy" / "total_consumption_by_facility.csv")
    meters = pd.read_csv(generated_root / "energy" / "energy_by_meter.csv")
    health_summary = pd.read_csv(generated_root / "health" / "tables" / "table2_health_data_quality.csv")
    health_facility = pd.read_csv(generated_root / "health" / "tables" / "annex_health_data_completeness.csv")
    payments = pd.read_csv(generated_root / "payments" / "facility_payment_summary.csv")
    payment_overall = pd.read_csv(generated_root / "payments" / "overall_payment_summary.csv")
    capex = pd.read_csv(generated_root / "payments" / "facility_capex_and_commitment.csv")
    tables = {
        "table_s2a_power_reliability_quality.csv": build_power_quality_table(figure3, reliability),
        "table_s2b_energy_consumption.csv": build_energy_table(totals, meters),
        "table_s3_facility_selection.csv": pd.read_csv(config_root / "study_facilities.csv"),
        "table_s6_health_data_quality.csv": health_summary.round(3),
        "table_s7_health_completeness_by_facility.csv": build_health_facility_table(health_facility),
        "table_s8_payment_performance_by_facility.csv": build_payment_table(payments),
        "table_s9_financial_summary.csv": payment_overall.round(2),
        "table_s10_facility_capex_commitment.csv": capex.round(2),
    }
    paths = {}
    for name, frame in tables.items():
        path = output_root / name
        frame.to_csv(path, index=False)
        paths[name] = path
    return paths
