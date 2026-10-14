# Figure 3 delivery and manuscript alignment

All six existing-supply comparison estimates in `publication/figure3/` are now reconstructed from sensor records. Historical transcriptions are retained only in `config/manuscript_pre_results.csv`; they are not the source of submission values. The workflow requires the longitudinal audit and fails if a selected baseline is absent.

## Baseline decisions

| Facility | Inherited uptime | Reconstructed uptime | Sensor/window basis |
|---|---:|---:|---|
| HGR1 | 97.9% | 99.06% | Two PowerWatch sensors; shared pre-source window |
| CH1 | 69.2% | 69.15% | One PowerWatch; artisanal-solar source comparison |
| CSR1 | 44.0% | 74.81% | Two PowerWatch sensors including DRC1 supplement; full available pre record, variable coverage |
| CSR2 | 14.9% | 14.34% | One PowerWatch; July old-solar source comparison |
| CSR3 | 95.0% | 95.75% | Two PowerWatch sensors; shared pre-source window through July 2023 |
| CSR4 | 72.8% | 72.83% | One PowerWatch; January grid/old-supply comparison |

Exact dates, inherited/reconstructed voltage and frequency estimates, percentage-point differences, sensor identities and coverage are in `baseline_value_audit.csv`. The three longitudinal window choices and their rationales are fixed in `config/figure3_baseline_selections.csv`. Individual, shared and full-record sensitivities are exported in `longitudinal_pre_comparisons.csv`.

CSR3's full-record expected-window sensitivity is 54.31%, but coverage is only 56.70%; observed uptime is 95.77%. The shared sensor window has 99.77% coverage and 95.75% expected-window uptime. Main-window selection is based on sensor overlap and coverage, not fitting a target manuscript number. CSR1's full record has 99.23% coverage by at least one sensor and 81.95% by both; its shared-window sensitivity is 75.17%.

The longitudinal cutoffs use configured intervention-source monitoring starts, not independently verified installation dates. CH1/CSR2/CSR4 comparisons are not uniformly pre-installation observations. CSR4's March HOP readings remain excluded because their historical source is unconfirmed. Labels therefore remain **Existing supply / Protected circuit**. The legend distinguishes single-PowerWatch comparisons from two-PowerWatch longitudinal baselines; it no longer marks inherited results.

## Files and reproduction

Run `python scripts/run_all.py --from-public` with the four checksum-verified telemetry archives imported. The DRC1 supplement supplies the second CSR1 baseline device. Run `python scripts/export_figure3.py` with the publication extra installed to update SVG, vector PDF and 3600-DPI PNG files at 7.5 inches wide.

- `figure3.svg/.pdf/.png`: combined submission figure.
- `figure3_summary.svg/.pdf/.png`: summary panels.
- `figure3_timeseries.svg/.pdf/.png`: CSR1 existing-grid and protected-core circuit traces, not a morgue-only trace.
- `figure3_independent_pqr_sensitivity.svg/.pdf/.png`: independent voltage/frequency denominators for all six comparisons and follow-up.
- `pre_post_summary.csv`: plotted values, pre/post sensor coverage and exact windows.
- `baseline_value_audit.csv`: all six inherited-to-reconstructed comparisons.
- `frequency_thresholds_joint.csv` and `frequency_thresholds_independent.csv`: complete ±0.1/1/5/10% results for all six facilities.
- Audit CSVs: source checksums, individual sensors, selected longitudinal baselines and alternative windows.
- `caption.txt`: replacement caption.

## Paste-ready methods

“We compared existing-supply observations with protected intervention-circuit observations. Existing-supply monitoring was not uniformly conducted before installation. CH1, CSR2 and CSR4 used single PowerWatch source comparisons. HGR1 and CSR3 used shared two-PowerWatch pre-source windows; CSR1 used the full available pre-source record from two PowerWatch devices with variable coverage. Cutoffs followed the configured start of intervention-source monitoring. We report exact windows, single-sensor alternatives, shared-window alternatives and sensor coverage. Two-minute bins were classified as powered when either contributing sensor recorded voltage >23 V. Powered bins were divided by expected bins in the selected window; observed-evidence uptime was supplied separately. Missing telemetry remained an unknown electrical state rather than a confirmed outage. Protected-circuit uptime used matched HOP and PowerWatch sensors. PQR used jointly valid voltage/frequency observations, with equal sensor means for longitudinal baselines and pooled source-sensor readings for follow-up; independent denominators were supplied as sensitivity. Voltage compliance was 207–253 V. The main frequency summary used 47.5–52.5 Hz (±5%); the illustrative trace highlighted 49.5–50.5 Hz (±1%). We additionally report ±0.1%, ±1% and ±10% compliance for all facilities.”

These are descriptive source comparisons with different monitoring periods and circuit locations, not a matched causal before/after analysis. HGR1's lower expected-window follow-up value must not be interpreted as demonstrated deterioration without considering source differences and missingness. Both-missing, single-low and double-low evidence remain separate in the follow-up audit. The manuscript must use the updated values and methods rather than the older screenshot/caption.
