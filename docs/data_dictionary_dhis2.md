# DHIS2 Public Data Dictionary

## Shared identifiers

- `facility_id_anonymized`: stable `FAC_T01`–`FAC_T06` or `FAC_C01`–`FAC_C06` identifier.
- `display_code`: manuscript display code. Treatment facilities retain the established `HGR1`, `CH1`, and `CSR1`–`CSR4` codes.
- `arm`: `treatment` or `control`.
- `facility_type`: `HGR`, `CH`, or `CSR`.
- `month`: calendar month in `YYYY-MM` format.

## Ward-month panel

One row per expected facility-month-ward for internal medicine, pediatrics,
surgery, and obstetrics/gynaecology.

- `admissions`: reported monthly admissions; missing remains blank.
- `admissions_reported`: whether DHIS2 contained an admission value.
- `deaths_before_48h`, `deaths_after_48h`: reported death components.
- `deaths_reported`: whether either death component was reported.
- `deaths_imputed_zero_from_missing`: both death components were blank and the canonical structural-zero rule was applied.
- `deaths_total`: before- plus after-48-hour deaths, with missing components contributing zero.
- `mortality_rate`: `deaths_total / admissions` where admissions are positive.
- `included_primary_analysis`: admissions were reported and at least five.
- `exclusion_reason`: deterministic reason for ward-level exclusion.

## Facility-month panel

One row per expected facility-month. Admissions and deaths are summed only
across wards with reported admissions, matching the canonical v3 notebook.
`facility_month_reported` is true when at least one included ward reported
admissions.
