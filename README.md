# North Kivu Health-Facility Power Analysis

Reproducible analysis of electricity reliability, conditional power quality,
and energy use across six anonymized health facilities in North Kivu, DRC.

This is a clean-room workflow scaffold derived from the documented analytical
requirements and approved anonymized release assets. Raw sensor data and the
private facility identity key are intentionally excluded from version control.

## Data locations at a glance

| Domain | Available directly on GitHub | Local authorized inputs (not on GitHub) | Analysis command |
|---|---|---|---|
| **HOP and PowerWatch electricity telemetry** | Sensor inclusion maps and analysis windows in `config/energy_meters.csv`, `config/paired_sensors.csv`, `config/canonical_powerwatch.csv`, and `config/analysis_periods.csv` | Authorized ZIP files in `data/raw/downloads/`, extracted under `data/raw/extracted/` | `python scripts/run_energy.py`, `python scripts/run_reliability.py`, and `python scripts/run_power_quality.py` |
| **Facility payment information** | Anonymized transaction ledger at `data/public/payments/payment_ledger_anonymized.csv` | Original identified financial records are not required by the public pipeline and are not tracked | `python scripts/run_payments.py` |
| **DHIS2 health data** | Anonymized ward-month and facility-month panels at `data/public/dhis2_ward_month_anonymized.csv` and `data/public/dhis2_facility_month_anonymized.csv` | Authorized raw exports in `data/raw/dhis2/` and the identity crosswalk in `config/private/` | `python scripts/run_health.py` |

The payment ledger and processed DHIS2 panels are included in the public GitHub
repository. The high-frequency HOP and PowerWatch files are **not** stored in
GitHub: they are larger authorized release assets, verified using
`config/data_sources.toml`, and remain local and Git-ignored. See
[`docs/DATA_GUIDE.md`](docs/DATA_GUIDE.md) for the complete file map and the
distinction between source data, tracked public data, configuration, and
generated outputs.

## Analytical principles

1. **Reliability and power quality are separate outcomes.** Availability asks
   whether usable power is present. Conditional power quality asks whether
   voltage/frequency are compliant while power is present.
2. **Missing telemetry is not automatically an outage.** Missing intervals are
   reported as unknown unless a named conservative sensitivity analysis says otherwise.
3. **Post-intervention confirmed outages use paired sensors.** A confirmed
   outage requires simultaneous outage evidence from co-located HOP and
   PowerWatch sensors.
4. **Every inclusion and time window is configured, not buried in notebook cells.**
5. **Private identities never enter public artifacts.** Public codes remain the
   stable analysis identifiers.

## Repository structure

```text
config/                 Public sensor map and reviewable analysis periods
src/drc_power/          Reusable ingestion and analysis modules
tests/                  Unit tests for key estimands
docs/                   Decisions, open questions, and audit trail
data/raw/               Local-only release assets (Git-ignored)
data/private/           Local-only identity key (Git-ignored)
data/public/            Tracked anonymized manuscript datasets
outputs/generated/      Reproducible generated tables and figures
```

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
pytest
```

## Add the raw data locally

Download the three authorized release ZIPs to your computer. They are verified
against the checksums in `config/data_sources.toml` and remain excluded from Git.

```bash
python scripts/bootstrap_data.py --source-dir ~/Downloads
```

Alternatively, set a machine-specific source location:

```bash
export DRC_DATA_DOWNLOADS="/path/to/authorized/release-zips"
python scripts/bootstrap_data.py
```

Use `--verify-only` to check files without copying or extracting them. The
resulting local structure is `data/raw/downloads/` plus `data/raw/extracted/`.

## Reproduce current analyses

After bootstrapping the data and installing the package:

```bash
python scripts/run_all.py
```

Or run analyses separately:

```bash
python scripts/run_power_quality.py
python scripts/run_reliability.py
python scripts/run_energy.py
python scripts/run_figure3_summary.py
python scripts/run_payments.py
python scripts/run_health.py
python scripts/run_annex.py
```

Generated CSVs and SVG figures are written to `outputs/generated/`. These are
currently labeled **provisional** because exact intervention windows, conflict
exclusions, and parts of the electrical topology remain under study-team review.

## Current status

- Raw-asset inventory complete.
- Seven PowerWatch original/updated pairs audited; each updated file is an
  exact superset of its original.
- Analysis primitives implemented and tested.
- Facility periods and exclusions remain provisional pending study-team review.
- Provisional power-quality, paired-reliability, and energy regeneration is available.
- Anonymized payment-ledger analysis and provisional Figure 6 are reproducible.
- Anonymized DHIS2 ward-month and facility-month panels, Table 2, QA reports,
  and an HGR1 health dashboard are reproducible.
- Annex-ready electricity, energy, facility-selection, health, payment, and
  capital tables are regenerated from the current outputs by `run_annex.py`.

## Rebuild the DHIS2 health panels

The public repository contains anonymized processed panels but not raw DHIS2
exports or the private facility crosswalk. Authorized analysts should place the
canonical files at:

```text
data/raw/dhis2/admissions.csv
data/raw/dhis2/deaths.csv
config/private/facility_crosswalk_private.csv
```

Then run `python scripts/run_health.py`. This regenerates:

- `data/public/dhis2_ward_month_anonymized.csv`;
- `data/public/dhis2_facility_month_anonymized.csv`;
- Table 2 and descriptive health tables;
- mapping, missingness, duplicate-column, and implausible-value QA reports; and
- the HGR1 descriptive dashboard.

The health analysis is descriptive. It evaluates whether routine reporting is
sufficiently complete and continuous for future infrastructure-health
evaluation; it does not estimate a causal treatment effect.
