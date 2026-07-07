# Data Guide

This guide answers two questions for each analytical domain:

1. Which files are available immediately after cloning the public repository?
2. Which authorized source files must be added locally before rebuilding an analysis?

## Storage classes

- **Tracked public data:** anonymized files committed to GitHub and available after cloning.
- **Local authorized data:** source files deliberately excluded by `.gitignore`; these must be obtained through the authorized study-data channel.
- **Configuration:** tracked, reviewable decisions about sensors, dates, topology, and inclusion.
- **Generated output:** reproducible tables and figures written under `outputs/generated/`; this directory is not committed because it can be rebuilt.

## HOP and PowerWatch electricity telemetry

### Local authorized source files

```text
data/raw/downloads/HOP_daily_energy.zip
data/raw/downloads/HOP_voltage_power_1min.zip
data/raw/downloads/PowerWatch_voltage_frequency_2min.zip
```

After `python scripts/bootstrap_data.py`, the archives are extracted to:

```text
data/raw/extracted/HOP_daily_energy/
data/raw/extracted/HOP_voltage_power_1min/
data/raw/extracted/PowerWatch_voltage_frequency_2min/
```

The HOP files provide daily energy and one-minute voltage/power measurements;
the PowerWatch files provide two-minute voltage/frequency measurements. Thus,
energy consumption is calculated from HOP, while paired reliability and power
quality use both platforms. These source files are
not committed to GitHub. Their expected filenames and SHA-256 checksums are
recorded in `config/data_sources.toml`.

### Tracked analytical configuration

```text
config/energy_meters.csv           HOP meters included in energy accounting
config/paired_sensors.csv          matched HOP–PowerWatch pairs
config/canonical_powerwatch.csv    canonical PowerWatch source selection
config/analysis_periods.csv        source starts and telemetry exclusions
config/manuscript_pre_results.csv  manuscript-reported baseline values awaiting reproduction
```

### Generated results

```text
outputs/generated/energy/
outputs/generated/reliability/
outputs/generated/power_quality/
outputs/generated/figure3/
```

Rebuild with:

```bash
python scripts/run_energy.py
python scripts/run_reliability.py
python scripts/run_power_quality.py
python scripts/run_figure3_summary.py
```

## Facility payment data

### Tracked public ledger

```text
data/public/payments/payment_ledger_anonymized.csv
```

This is the transaction-level analytical ledger used for payment revenue,
remittance timing, operating expenditure, subsequent CAPEX, and cumulative
cash-balance calculations. It uses the same public facility codes as the energy
analysis: `HGR1`, `CH1`, and `CSR1`–`CSR4`.

Reference financial assumptions are stored in:

```text
config/capex_reference.csv
config/capex_components.csv
config/facility_financial_reference.csv
```

Generated payment tables and figures are written to:

```text
outputs/generated/payments/
```

Rebuild with:

```bash
python scripts/run_payments.py
```

## DHIS2 health data

### Tracked public analytical panels

```text
data/public/dhis2_ward_month_anonymized.csv
data/public/dhis2_facility_month_anonymized.csv
```

The ward-month panel contains the four standardized ward groups used for
cleaning and mortality construction. The facility-month panel contains the
aggregated admissions, deaths, mortality, ward-coverage, and reporting flags
used for Table 2 and descriptive dashboards.

### Local authorized source files

```text
data/raw/dhis2/admissions.csv
data/raw/dhis2/deaths.csv
data/raw/dhis2/canonical_notebook.ipynb
config/private/facility_crosswalk_private.csv
```

The raw exports and identity crosswalk are not committed to GitHub. The public
panels can be inspected immediately after cloning, but regenerating them from
source requires these authorized local files.

Generated health tables, QA reports, and figures are written to:

```text
outputs/generated/health/
```

Rebuild with:

```bash
python scripts/run_health.py
```

## Rebuild everything

Once the authorized local electricity and DHIS2 source files are present:

```bash
python scripts/run_all.py
```

This runs the electricity, energy, payment, health, figure-summary, and annex
pipelines. It does not place raw or identified files under version control.
