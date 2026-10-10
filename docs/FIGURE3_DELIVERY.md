# Figure 3 delivery and manuscript alignment

The delivery in `publication/figure3/` preserves the original layout, colours,
and three-panel comparison. It is a transparent revision, not certification of
all six inherited baselines.

## Targeted corrections

- CH1, CSR2, and CSR4 comparison numbers come from local sensor records rather
  than transcribed manuscript results. CSR2 uptime changes from 14.9% to 14.34%;
  CH1 is 69.15% and CSR4 is 72.83% using two-minute medians.
- The x-axis says **Existing supply / Protected circuit**. July CSR2 and January
  CSR4 are observations after broad deployment, and CH1's inherited window
  spans deployment; they cannot uniformly be described as pre-installation data.
- CSR4 March HOP data is not used because its historical supply is unconfirmed.
  Concurrent HOP/PW records are paired only for mapped co-source follow-up.
- The study author confirmed on 10 October 2026 that CH1's comparison sensor
  remained on artisanal solar, CSR2's July sensor monitored old solar, and
  CSR4's January sensor monitored the grid/old supply. The comparison source
  assignments are recorded in configuration and exported provenance.
- Main voltage PQR uses the inherited joint-validity policy consistently in
  reconstructed comparisons and follow-up. This preserves comparability with
  the existing chart; separate-denominator voltage PQR is supplied as sensitivity.
- Summary frequency remains **±5%**, exactly as previously plotted. The top
  trace band changes from unlabelled **±2%** to explicitly labelled **±1%**.
  On 10 October 2026 the study author selected retaining the ±5% summary with
  ±1% and ±10% reported additionally.
- HGR1, CSR1, and CSR3 inherited baseline values carry a dagger and remain
  awaiting independent reconstruction. No missing ±1%/±10% baseline values are
  fabricated from the inherited ±5% percentages.

## Files

- `figure3.svg/.png/.pdf`: combined figure.
- `figure3_summary.svg/.png/.pdf`: main comparable summary.
- `figure3_timeseries.svg/.png/.pdf`: CSR1 trace.
- `figure3_independent_pqr_sensitivity.svg/.png/.pdf`: voltage/frequency
  denominators kept separate for the reconstructed comparisons and follow-up;
  the three inherited baselines are explicitly unchanged.
- `pre_post_summary.csv`: actual values and provenance behind the main summary.
- `frequency_thresholds_joint.csv` and `frequency_thresholds_independent.csv`:
  ±1%, ±5%, and ±10% estimates, with unavailable baselines blank.
- `single_sensor_comparisons.csv`, `post_sensor_comparison.csv`, `input_inventory.csv`:
  audit evidence and exact source checksums.
- `caption.txt`: replacement figure caption.

PNGs are 600 DPI at 7.5 inches wide. SVGs and PDFs are vector sources.

## Paste-ready methods clarification

“We compared existing-supply observations with protected intervention-circuit
observations. Existing-supply monitoring was not uniformly conducted before
installation: the short source-specific comparisons at CH1, CSR2, and CSR4 used
single PowerWatch sensors during the documented comparison windows. Protected-
circuit uptime used matched HOP and PowerWatch sensors, with two-minute bins
classified as powered when either recorded voltage >23 V. We report powered bins
as a proportion of all expected bins in the shared valid monitoring window, and
provide an observed-evidence denominator and sensor coverage as sensitivity
analyses. Missing telemetry was retained as an unknown electrical state, not
classified as a confirmed electrical outage. PQR in the comparable Figure 3
summary was calculated among observations with both valid voltage and valid
frequency; we also evaluated separate voltage and frequency denominators.
Voltage compliance was 207–253 V. The summary frequency panel used 47.5–52.5 Hz
(±5% of 50 Hz); the illustrative trace highlighted 49.5–50.5 Hz (±1%). We provide
±1%, ±5%, and ±10% results where the source observations support reconstruction.”

This wording describes the plotted analyses. It should replace the manuscript's
current blanket pre/post wording and statement that only ±1%/±10% were evaluated
if this version of the figure is selected. The remaining inherited longitudinal
baselines still need source-based verification before submission.

## Next submission item: frequency-threshold consistency

The existing manuscript describes ±1% and ±10%, the original summary figure
shows ±5%, and the old illustrative trace band was ±2%. The regenerated delivery
makes these definitions explicit and supplies all threshold tables. It does not
claim complete six-facility ±1%/±10% baseline reconstruction. To use ±1% or ±10%
as the primary six-facility summary, first reconstruct the three longitudinal
baselines from reviewed source windows. This is an analytical requirement rather
than a cosmetic axis-label change.

## Uptime-definition reconciliation

The primary runner and audit now share a single implementation of the paired
expected-window and observed-evidence estimates. Configured excluded calendar
bins are removed explicitly, so resampling cannot reintroduce a removed period
as missing telemetry. The output distinguishes both-observed low-voltage bins,
one-observed low-voltage bins, discordant bins, and both-missing bins, and reports
two-sensor coverage. The audit includes all seven mapped follow-up pairs across
the six facilities, including the non-primary CSR3 circuit. These changes do not
alter the numerator definition: either co-source sensor reporting >23 V is
powered. Concordant-pair availability remains a separately named diagnostic.
