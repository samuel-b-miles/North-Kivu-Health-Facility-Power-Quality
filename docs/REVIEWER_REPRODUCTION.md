# Reviewer Reproduction Guide

This guide describes the shortest path from the public repository plus an
authorized restricted-data bundle to regenerated manuscript tables and figures.

## What is public

The public repository includes the analysis code, tests, configuration files,
anonymized DHIS2 analytical panels, and anonymized payment ledger. These files
are enough to inspect the workflow, run unit tests, and reproduce analyses that
depend only on public processed data.

## What requires restricted data

Full source-level reproduction also requires restricted local inputs:

- HOP daily energy ZIP
- HOP one-minute voltage/power ZIP
- PowerWatch two-minute voltage/frequency ZIP
- raw DHIS2 admissions export
- raw DHIS2 deaths export
- private facility crosswalk

The required filenames, local destinations, classifications, and SHA-256
checksums are listed in `config/restricted_data_sources.csv`.

## Quickstart

Clone the public analysis repository:

```bash
git clone https://github.com/samuel-b-miles/North-Kivu-Health-Facility-Power-Quality.git
cd North-Kivu-Health-Facility-Power-Quality
```

Create the Python environment:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
```

Download or clone the authorized restricted-data bundle to a local folder. Then
copy, verify, and extract the restricted inputs:

```bash
python scripts/prepare_restricted_data.py --source /path/to/restricted-data-bundle
```

Run the tests:

```bash
pytest
```

Rebuild all analyses:

```bash
python scripts/run_all.py
```

Generated outputs are written to `outputs/generated/`.

## Restricted-data bundle layout

The preparation script accepts either the canonical restricted repository layout
or a folder containing uniquely named source files. The canonical layout is:

```text
data/restricted/electricity/v2.0/HOP_daily_energy.zip
data/restricted/electricity/v2.0/HOP_voltage_power_1min.zip
data/restricted/electricity/v2.0/PowerWatch_voltage_frequency_2min.zip
data/restricted/dhis2/v1.0/admissions.csv
data/restricted/dhis2/v1.0/deaths.csv
data/private/facility_crosswalk_private.csv
```

These files are copied into Git-ignored local paths expected by the analysis
scripts:

```text
data/raw/downloads/
data/raw/extracted/
data/raw/dhis2/
config/private/
```

## Access note

Raw DHIS2 exports and the private facility crosswalk contain identified facility
information or can reconstruct it. They should be shared only through the
authorized study-data channel and under the approvals described in the
manuscript data availability statement.
