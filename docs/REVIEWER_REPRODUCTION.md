# Reproduction guide

## Choose the analysis version

The default branch `main` is an earlier snapshot. Current submission results use
[`61b8a328`](https://github.com/samuel-b-miles/North-Kivu-Health-Facility-Power-Quality/tree/61b8a328b06e9d198fd9469dde0278128933172d) on `submission-six-facility-baselines`.
Check out that commit before using `--from-public` or the four-archive workflow.
The README contains the clone and environment setup commands.

## Current submission: public inputs

After installing the pinned version with `pip install -e '.[dev]'`:

```bash
pytest
python scripts/run_payments.py
python scripts/run_health.py --from-public
python scripts/run_timeline_figure.py
```

Payments use the tracked anonymized ledger. Health outputs use the tracked
ward-month panel and rebuild facility-month aggregates. This mode does not
recreate identified-source mapping or duplicate-column audits.

## Current submission: electricity inputs

Obtain the four authorized archives listed in the pinned version's
[`config/data_sources.toml`](https://github.com/samuel-b-miles/North-Kivu-Health-Facility-Power-Quality/blob/61b8a328b06e9d198fd9469dde0278128933172d/config/data_sources.toml).
Then verify, copy, and extract them:

```bash
python scripts/bootstrap_data.py --source-dir /path/to/authorized/archives
python scripts/run_all.py --from-public
```

`--verify-only` checks archives without copying or extracting. Telemetry remains
under Git-ignored `data/raw/downloads/` and `data/raw/extracted/`. The full runner
requires telemetry even when health inputs come from public panels.

The complete companion package is a local candidate, not a verified public
deposit. Its `run_public_package.py` requires the package manifest and included
archives; it is not a substitute for missing inputs in a GitHub clone.

## Manuscript output map

| Output | Entry point | Generated directory |
|---|---|---|
| Figure 2 implementation/analysis timeline | `run_timeline_figure.py` | `timeline/` |
| Figure 3 reliability and power quality | `run_power_quality.py`, `run_reliability.py`, `run_baseline_audit.py`, `run_longitudinal_pre_audit.py`, `run_figure3_summary.py`, `run_figure3_timeseries.py` | `power_quality/`, `reliability/`, `baseline_audit/`, `figure3/` |
| Figure 4 energy use | `run_energy.py` | `energy/` |
| Figure 6 payments and capital costs | `run_payments.py` | `payments/` |
| Table 2 health reporting and descriptive dashboard | `run_health.py --from-public` | `health/` |
| Supplementary tables | `run_annex.py` after upstream analyses | `annex/` |

All directories above are under `outputs/generated/`. Run the Figure 3 summary
with `--pqr-policy independent` for its denominator sensitivity; the default
summary uses jointly valid voltage/frequency observations. Publication exports
and exact provenance are documented in the pinned version's
[Figure 3 guide](https://github.com/samuel-b-miles/North-Kivu-Health-Facility-Power-Quality/blob/61b8a328b06e9d198fd9469dde0278128933172d/docs/FIGURE3_DELIVERY.md).
This map covers implemented outputs, not every manuscript claim.

## Source-level health cleaning

Authorized analysts can use `prepare_restricted_data.py --source /path/to/bundle`
to prepare raw DHIS2 exports and the private facility crosswalk, with checksums
from `config/restricted_data_sources.csv`. Run `run_health.py` without
`--from-public` to clean those sources and regenerate the panels and source QA.
Keep identified inputs and mapping audits within the authorized study-data channel.

## Earlier default-branch snapshot

On `main`, `run_payments.py` and `run_timeline_figure.py` require no restricted
inputs. `run_health.py` requires raw admissions/deaths and the private crosswalk;
it does not support `--from-public`. Electricity bootstrapping uses the three
archives listed in `main`'s `config/data_sources.toml`. With those inputs and the
restricted health sources prepared, `python scripts/run_all.py` runs that earlier
snapshot. Its baseline and frequency results differ from the current submission.
