# Full-resolution telemetry release preparation

Build the local candidate from the four checksum-verified archives:

```bash
python scripts/build_public_telemetry_release.py --output-dir outputs/release_candidate/telemetry-v1
```

The output directory must be new. Incomplete builds remain local and must not be published. Successful builds contain `manifest.json`, four ZIPs, an import configuration and a README. The generated manifest independently verifies output rows and every retained source value. Archive entries have fixed timestamps and no source path/comment metadata.

Retain complete coded measurement files, not illustrative snippets. GridWatch outputs contain time, voltage and frequency only. HOP voltage files retain time, total and phase fields; daily-energy files retain Time and Energy per Day. Values, timestamp strings, row order, duplicates, blanks, and original/updated version distinctions remain unchanged. Include omitted files for transparency while preserving their exclusion status. Do not concatenate overlapping export versions.

Remove respondent/site strings, summary/location notes and derived time differences. Exclude the energy export lacking a safe coded sensor filename. No identified DHIS2 files or identity crosswalks enter this package. Public health/payment panels remain separate; approval of this electricity candidate does not approve expanded health disclosure.

## Student exercise supplied by the author

The Drive folder inspected on 10 October 2026 contains a 1.77 GB voltage/frequency CSV and a site mapping file. The mapping explicitly links names to codes and must not accompany an anonymised public release. Its code namespace differs from the six-facility implementation pilot, so its identifiers must not be joined directly to this repository. The connector could not fetch the large CSV (HTTP 413); its transformation, completeness and accuracy have not been verified. The pilot candidate is therefore built from the locally verified pilot archives.

## Release boundaries

This is coded/deidentified data, not a claim of irreversible anonymity. Exact calendar dates and facility/sensor patterns remain to preserve reproduction and require partner disclosure review. Proposed public licence: CC BY 4.0; code: MIT. Confirm rights holders and attribution before attaching final licence notices or depositing publicly. An open licence would permit reuse without individual approval, so only approved public data should receive it.

The archives retain filenames/schema compatible with existing electricity workflows. Import with:

```bash
python scripts/bootstrap_data.py --source-dir /path/to/candidate --config /path/to/candidate/data_sources.toml --raw-dir /tmp/pilot-public-raw
python scripts/run_energy.py --raw-root /tmp/pilot-public-raw/extracted
python scripts/run_reliability.py --raw-root /tmp/pilot-public-raw/extracted
python scripts/run_power_quality.py --raw-root /tmp/pilot-public-raw/extracted
python scripts/run_baseline_audit.py --raw-root /tmp/pilot-public-raw/extracted
python scripts/run_figure3_summary.py
python scripts/run_figure3_timeseries.py --raw-root /tmp/pilot-public-raw/extracted
```

Use a separate output root for verification where supported. The recovered DRC1 sensor resolves the missing CSR1 baseline input. Archive completeness does not establish installation dates, causal comparability or energy topology. Preserve those limitations in the manuscript and release metadata.

## Local candidate validation (10 October 2026)

`outputs/release_candidate/telemetry-v1-reviewed/` contains 46 files and 20,196,654 rows, compressed to 112,044,336 bytes. Three source archive checksums passed. All retained cells/rows passed independent archive readback verification. Import into a separate empty raw-data tree succeeded; the energy and baseline-audit workflows ran against the candidate. The energy meter, facility, daily and monthly outputs and baseline single/paired comparison tables match original-input outputs exactly. All 28 tests passed, including release filename/schema and value-validation checks. The candidate remains local and is not an approved public deposit.

## Six-baseline revision

`telemetry-v2-six-baselines` adds the verified DRC1-derived CSR1-PW-01 series. Four archives contain 47 coded measurement files and 20,602,408 rows (116,608,466 compressed bytes). Every retained row/value passed full archive readback. The earlier v1 counts above describe the earlier snapshot. All six figure baselines now reconstruct from these inputs.
