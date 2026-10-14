# Electricity and payment release dictionary

## Electricity source readings

Coded sensor IDs in filenames link to `config/paired_sensors.csv`, `energy_meters.csv` and `canonical_powerwatch.csv`. IDs encode facility and platform, not original hardware IDs. Original and updated GridWatch exports overlap; use canonical selection. Files labelled omitted remain excluded unless a separately documented decision changes this.

| File class | Fields and interpretation |
|---|---|
| GridWatch | `time`: source timestamp, generally UTC-explicit; `voltage`: volts; `frequency`: hertz. Retain anomalies and blanks; cleaning is done by code. |
| HOP voltage | `time`: source timestamp; `total`, `phase_1`, `phase_2`, `phase_3`: source voltage fields, including unit suffixes where present. Use loader rules; blank means unreported, not zero. |
| HOP daily energy | `Time`: source day timestamp; `Energy per Day`: daily energy retaining Wh/kWh/MWh text. Initial zero records before the first positive reading are treated as inactive by the energy runner. |

Naive HOP times are interpreted as UTC by the existing pipeline; device clock timezone has not been independently established. Values are neither shifted nor resampled in the raw release. Analysis windows/exclusions are in `analysis_periods.csv` and `baseline_audit_windows.csv`. Two-minute medians, the >23 V powered threshold, expected-window versus observed-evidence uptime, joint-valid quality denominators and ±1/5/10% frequency thresholds are documented in `UPTIME_METHODS.md` and `FIGURE3_DELIVERY.md`.

## Payment analysis ledger

| Field | Meaning |
|---|---|
| `date` | Calendar transaction date used for monthly aggregation |
| `facility` | Public facility code or `ADMIN` |
| `transaction_direction` | `inflow` or `outflow` |
| `transaction_category` | Recorded analytical expense/revenue category; additional upgrades are separated from OPEX |
| `amount_received_usd` | Amount received in USD |
| `amount_paid_usd` | Amount paid in USD |
| `days_late` | Recorded remittance delay in days; missing delay is treated as zero by the current calculation |
| `is_additional_system_capex` | Recorded upgrade flag; main expenditure classification uses category |

The candidate excludes `external_id`, `capex_note` and `description_original`. It preserves all financial calculation fields. Dates and amounts may identify transactions to people with outside knowledge; financial release permissions remain to be confirmed. Reference CAPEX/commitment assumptions are in the corresponding config CSVs.

## Health panels

See `data_dictionary_dhis2.md`. Ward and facility values are aggregate counts, not individual patient records. Missing deaths may be imputed to zero under the documented source-cleaning rule; flags are retained. Small counts and shared codes require review. Suppression or temporal transformations must be explicit and their effects on reproduction documented.
