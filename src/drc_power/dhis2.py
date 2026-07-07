"""Deterministic DHIS2 cleaning, anonymization, QA, and Table 2 estimands."""

from __future__ import annotations

import re
import unicodedata
from pathlib import Path

import numpy as np
import pandas as pd

PUBLIC_ID_PATTERN = re.compile(r"^FAC_[TC][0-9]{2}$")


def normalize_string(value: object) -> str:
    if pd.isna(value):
        return ""
    text = unicodedata.normalize("NFKD", str(value).lower().strip()).encode("ascii", "ignore").decode()
    return re.sub(r"\s+", " ", text)


def read_parameters(path: Path) -> dict[str, str]:
    frame = pd.read_csv(path)
    return dict(zip(frame["parameter"], frame["value"].astype(str)))


def parse_month(values: pd.Series) -> pd.Series:
    return pd.to_datetime(values.astype("Int64").astype(str), format="%Y%m", errors="coerce")


def duplicate_pairs(columns: list[str]) -> list[tuple[str, str]]:
    column_set = set(columns)
    return [(column[:-2], column) for column in columns if column.endswith(".1") and column[:-2] in column_set]


def audit_duplicate_columns(frame: pd.DataFrame, dataset: str) -> pd.DataFrame:
    rows = []
    for base, duplicate in duplicate_pairs(list(frame.columns)):
        first = pd.to_numeric(frame[base], errors="coerce")
        second = pd.to_numeric(frame[duplicate], errors="coerce")
        rows.append({
            "dataset": dataset,
            "base_column": base,
            "duplicate_column": duplicate,
            "both_missing_n": int((first.isna() & second.isna()).sum()),
            "base_only_n": int((first.notna() & second.isna()).sum()),
            "duplicate_only_n": int((first.isna() & second.notna()).sum()),
            "identical_n": int((first.notna() & second.notna() & first.eq(second)).sum()),
            "conflict_n": int((first.notna() & second.notna() & first.ne(second)).sum()),
            "resolution": "later_duplicate_precedence_then_base",
        })
    return pd.DataFrame(rows)


def matching_columns(columns: list[str], search_terms: str, required: str | None = None) -> list[str]:
    terms = [normalize_string(value) for value in search_terms.split("|")]
    result = []
    for column in columns:
        normalized = normalize_string(column)
        if any(term in normalized for term in terms) and (required is None or required in normalized):
            result.append(column)
    return result


def coalesce_duplicate_indicator(frame: pd.DataFrame, columns: list[str]) -> pd.Series:
    if not columns:
        return pd.Series(np.nan, index=frame.index, dtype="float64")
    ordered = list(dict.fromkeys(columns))
    result = pd.to_numeric(frame[ordered[0]], errors="coerce")
    for column in ordered[1:]:
        result = pd.to_numeric(frame[column], errors="coerce").combine_first(result)
    return result


def coalesce_row(row: pd.Series | None, columns: list[str]) -> float:
    if row is None or not columns:
        return np.nan
    result = np.nan
    for column in columns:
        value = pd.to_numeric(pd.Series([row[column]]), errors="coerce").iloc[0]
        if pd.notna(value):
            result = value
    return result


def load_private_crosswalk(path: Path) -> pd.DataFrame:
    crosswalk = pd.read_csv(path, dtype=str).fillna("")
    crosswalk["raw_name_normalized"] = crosswalk["raw_facility_name"].map(normalize_string)
    crosswalk["include_study"] = crosswalk["include_study"].str.lower().eq("true")
    included = crosswalk[crosswalk["include_study"]]
    if len(included) != 12 or not included["facility_id_anonymized"].map(lambda value: bool(PUBLIC_ID_PATTERN.match(value))).all():
        raise ValueError("Private crosswalk must contain exactly 12 valid included public IDs")
    return crosswalk


def build_ward_month(
    admissions_path: Path,
    deaths_path: Path,
    crosswalk_path: Path,
    wards_path: Path,
    parameters_path: Path,
) -> tuple[pd.DataFrame, dict[str, pd.DataFrame | tuple[int, int] | int]]:
    admissions = pd.read_csv(admissions_path)
    deaths = pd.read_csv(deaths_path)
    raw_admissions_shape = admissions.shape
    raw_deaths_shape = deaths.shape
    admissions.columns = admissions.columns.str.strip()
    deaths.columns = deaths.columns.str.strip()
    for frame in (admissions, deaths):
        frame["raw_name_normalized"] = frame["organisationunitname"].map(normalize_string)
        frame["month_date"] = parse_month(frame["periodid"])

    crosswalk = load_private_crosswalk(crosswalk_path)
    included_crosswalk = crosswalk[crosswalk["include_study"]].copy()
    mapping = included_crosswalk.set_index("raw_name_normalized")
    wards = pd.read_csv(wards_path)
    parameters = read_parameters(parameters_path)
    start = pd.Timestamp(parameters["observation_start"] + "-01")
    end = pd.Timestamp(parameters["observation_end"] + "-01")
    minimum = int(parameters["ward_min_admissions"])

    admissions_lookup = admissions.set_index(["raw_name_normalized", "month_date"], drop=False)
    deaths_lookup = deaths.set_index(["raw_name_normalized", "month_date"], drop=False)
    expected_months = pd.date_range(start, end, freq="MS")
    rows = []
    for raw_name, meta in mapping.iterrows():
        for month in expected_months:
            admission_row = admissions_lookup.loc[(raw_name, month)] if (raw_name, month) in admissions_lookup.index else None
            death_row = deaths_lookup.loc[(raw_name, month)] if (raw_name, month) in deaths_lookup.index else None
            if isinstance(admission_row, pd.DataFrame) or isinstance(death_row, pd.DataFrame):
                raise ValueError(f"Duplicate raw facility-month row for {meta['facility_id_anonymized']} {month:%Y-%m}")
            for _, ward_meta in wards.iterrows():
                ward = ward_meta["ward"]
                admission_columns = matching_columns(list(admissions.columns), ward_meta["search_terms"])
                before_columns = matching_columns(list(deaths.columns), ward_meta["search_terms"], "avant 48")
                after_columns = matching_columns(list(deaths.columns), ward_meta["search_terms"], "apres 48")
                admission_value = coalesce_row(admission_row, admission_columns)
                before_value = coalesce_row(death_row, before_columns)
                after_value = coalesce_row(death_row, after_columns)
                admissions_reported = pd.notna(admission_value)
                deaths_reported = pd.notna(before_value) or pd.notna(after_value)
                deaths_total = (0 if pd.isna(before_value) else before_value) + (0 if pd.isna(after_value) else after_value)
                mortality = deaths_total / admission_value if admissions_reported and admission_value > 0 else np.nan
                reasons = []
                if not admissions_reported:
                    reasons.append("missing_admissions")
                elif admission_value < minimum:
                    reasons.append("admissions_below_5")
                rows.append({
                    "facility_id_anonymized": meta["facility_id_anonymized"],
                    "display_code": meta["display_code"],
                    "arm": meta["arm"],
                    "facility_type": meta["facility_type"],
                    "month": month.strftime("%Y-%m"),
                    "ward": ward,
                    "admissions": admission_value,
                    "admissions_reported": admissions_reported,
                    "deaths_before_48h": before_value,
                    "deaths_after_48h": after_value,
                    "deaths_reported": deaths_reported,
                    "deaths_imputed_zero_from_missing": not deaths_reported,
                    "deaths_total": deaths_total,
                    "mortality_rate": mortality,
                    "included_primary_analysis": admissions_reported and admission_value >= minimum,
                    "exclusion_reason": ";".join(reasons),
                })
    ward_month = pd.DataFrame(rows).sort_values(["facility_id_anonymized", "month", "ward"])
    audit = {
        "raw_admissions_shape": raw_admissions_shape,
        "raw_deaths_shape": raw_deaths_shape,
        "unique_raw_facilities": admissions["organisationunitname"].nunique(),
        "duplicate_columns": pd.concat([
            audit_duplicate_columns(admissions, "admissions"),
            audit_duplicate_columns(deaths, "deaths"),
        ], ignore_index=True),
        "crosswalk": crosswalk,
        "raw_admissions": admissions,
        "raw_deaths": deaths,
    }
    return ward_month, audit


def build_facility_month(ward_month: pd.DataFrame) -> pd.DataFrame:
    rows = []
    group_columns = ["facility_id_anonymized", "display_code", "arm", "facility_type", "month"]
    for keys, group in ward_month.groupby(group_columns, sort=True):
        reported = group["admissions_reported"]
        admissions = group.loc[reported, "admissions"].sum(min_count=1)
        deaths_total = group.loc[reported, "deaths_total"].sum(min_count=1)
        row = dict(zip(group_columns, keys))
        row.update({
            "wards_expected": 4,
            "wards_reported": int(reported.sum()),
            "facility_month_reported": bool(reported.any()),
            "admissions": admissions,
            "deaths_total": deaths_total,
            "mortality_rate": deaths_total / admissions if pd.notna(admissions) and admissions > 0 else np.nan,
            "included_primary_analysis": bool(reported.any()),
            "exclusion_reason": "" if reported.any() else "no_wards_reported",
        })
        rows.append(row)
    return pd.DataFrame(rows).sort_values(["facility_id_anonymized", "month"])


def longest_streak(values: pd.Series) -> int:
    best = current = 0
    for value in values.astype(bool):
        current = current + 1 if value else 0
        best = max(best, current)
    return best


def table2_metrics(ward_month: pd.DataFrame, facility_month: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for arm in ("treatment", "control"):
        wards = ward_month[ward_month["arm"] == arm]
        facilities = facility_month[facility_month["arm"] == arm]
        reported = facilities[facilities["facility_month_reported"]].copy()
        streaks = facilities.groupby("facility_id_anonymized")["facility_month_reported"].apply(longest_streak)
        rows.append({
            "arm": arm,
            "facility_month_reporting_completeness_pct": 100 * facilities["facility_month_reported"].mean(),
            "ward_month_reporting_completeness_pct": 100 * wards["admissions_reported"].mean(),
            "facilities_with_uninterrupted_reporting_n": int((streaks == 36).sum()),
            "facilities_total_n": int(streaks.size),
            "median_longest_continuous_reporting_streak_months": float(streaks.median()),
            "facility_months_with_deaths_pct": 100 * reported["deaths_total"].gt(0).mean(),
            "mean_monthly_admissions": reported["admissions"].mean(),
            "mean_inpatient_mortality_rate_pct": 100 * reported["mortality_rate"].mean(),
        })
    return pd.DataFrame(rows)


def missing_months(facility_month: pd.DataFrame) -> pd.DataFrame:
    missing = facility_month[~facility_month["facility_month_reported"]]
    return missing[["facility_id_anonymized", "display_code", "arm", "month"]].reset_index(drop=True)


def implausible_values(ward_month: pd.DataFrame) -> pd.DataFrame:
    reasons = []
    for _, row in ward_month.iterrows():
        flags = []
        if pd.notna(row["admissions"]) and row["admissions"] < 0:
            flags.append("negative_admissions")
        if row["deaths_total"] < 0:
            flags.append("negative_deaths")
        if pd.notna(row["admissions"]) and row["deaths_total"] > row["admissions"]:
            flags.append("deaths_greater_than_admissions")
        if flags:
            record = row.to_dict(); record["qa_flag"] = ";".join(flags); reasons.append(record)
    return pd.DataFrame(reasons)
