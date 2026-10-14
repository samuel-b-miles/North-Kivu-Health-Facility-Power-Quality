# North Kivu Health-Facility Power Analysis

Code and anonymized data for studying electricity reliability, power quality,
energy use, payments, and routine health reporting in North Kivu, DRC. Electricity
analyses cover six facilities; the DHIS2 panels cover twelve facilities.

**Terminology:** HOP (the hardware name used in the data files) and Prospect
(the platform developer named in the manuscript) refer to the same monitoring
stream in this project. Hardware and platform are distinct; filenames and sensor
IDs retain `HOP`. GridWatch supplies the separate voltage/frequency stream.

GridWatch is the reader-facing name for this monitoring stream. Historical
`PowerWatch` names in filenames, configuration, code identifiers and source
schemas are retained so reproduction commands continue to work.

## Current version

The current submission analysis is on
[`submission-six-facility-baselines`](https://github.com/samuel-b-miles/North-Kivu-Health-Facility-Power-Quality/tree/submission-six-facility-baselines),
pinned at [`61b8a328`](https://github.com/samuel-b-miles/North-Kivu-Health-Facility-Power-Quality/tree/61b8a328b06e9d198fd9469dde0278128933172d) (14 October 2026).
It reconstructs all six Figure 3 source comparisons and reports frequency
compliance at ±0.1%, ±1%, ±5%, and ±10% of 50 Hz. See its
[frequency methods and provenance](https://github.com/samuel-b-miles/North-Kivu-Health-Facility-Power-Quality/blob/61b8a328b06e9d198fd9469dde0278128933172d/docs/FREQUENCY_REPORTING.md).

`main` contains an earlier analysis snapshot. Its code and figures have not been
replaced by the submission revision. Use the pinned version for current results
and the [reproduction guide](docs/REVIEWER_REPRODUCTION.md) for version-specific commands.
The complete data package remains a release candidate pending rights and
disclosure review. No published Zenodo record or DOI is asserted here.

## Contents and access

| Contents | Available on GitHub | Additional inputs |
|---|---|---|
| Electricity and energy | Code, sensor maps, analysis windows, Figure 3 snapshots | Authorized telemetry archives |
| Payments | Anonymized transaction ledger and financial configuration | None for the public analysis |
| Health reporting | Anonymized ward-month and facility-month DHIS2 panels | Identified exports and private crosswalk only for source cleaning |

The public datasets are in [`data/public/`](data/public/), analysis settings in
[`config/`](config/), reusable code in [`src/drc_power/`](src/drc_power/), and
entry points in [`scripts/`](scripts/). Generated tables and SVG figures go to
`outputs/generated/` and are Git-ignored. See the [data guide](docs/DATA_GUIDE.md)
for filenames, checksums, and access boundaries.

## Reproduce

Use Python 3.11 or newer for the current submission version:

```bash
git clone https://github.com/samuel-b-miles/North-Kivu-Health-Facility-Power-Quality.git
cd North-Kivu-Health-Facility-Power-Quality
git checkout 61b8a328b06e9d198fd9469dde0278128933172d
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
pytest
python scripts/run_payments.py
python scripts/run_health.py --from-public
```

These payment and health commands use tracked anonymized data. Electricity
reproduction also requires the four authorized archives listed in that version's
`config/data_sources.toml`:

```bash
python scripts/bootstrap_data.py --source-dir /path/to/authorized/archives
python scripts/run_all.py --from-public
```

The [reproduction guide](docs/REVIEWER_REPRODUCTION.md) maps commands to manuscript
outputs and explains source-level DHIS2 cleaning. Figure 3 provenance is stored
with the [current figure files](https://github.com/samuel-b-miles/North-Kivu-Health-Facility-Power-Quality/tree/61b8a328b06e9d198fd9469dde0278128933172d/publication/figure3).

## Interpretation

Reliability and conditional power quality use different denominators. Missing
telemetry is an unknown electrical state; it is not evidence of an outage.
Paired expected-window uptime counts missing bins against availability, while
observed-evidence uptime reports coverage separately. Sensor selection, source
windows, and exclusions are configured and auditable.

Health reporting analyses are descriptive and do not estimate a causal treatment
effect. Source-window comparability, telemetry gaps, energy topology, and active
windows remain limitations; see the pinned version's
[baseline audit](https://github.com/samuel-b-miles/North-Kivu-Health-Facility-Power-Quality/blob/61b8a328b06e9d198fd9469dde0278128933172d/docs/LONGITUDINAL_PRE_AUDIT.md)
and [release limitations](https://github.com/samuel-b-miles/North-Kivu-Health-Facility-Power-Quality/blob/61b8a328b06e9d198fd9469dde0278128933172d/docs/PUBLIC_PACKAGE_REPRODUCTION.md).
