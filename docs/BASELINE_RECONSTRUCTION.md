# Figure 3: short-source comparison reconstruction

Audit date: 10 October 2026. Scope: CH1, CSR2, and CSR4, the three facilities
without the longitudinal baseline series. These results reconstruct the
available observations; they do not establish commissioning dates or prove
that a sensor monitored a particular source at an earlier time.

On 10 October 2026, the study author confirmed the comparison assignments:
CH1's comparison sensor remained on artisanal solar; CSR2's July sensor was on
old solar; CSR4's January sensor was on the grid/old supply. The comparisons
therefore have study-team-confirmed source identity, while commissioning dates
and the excluded March CSR4 HOP assignment are separate questions.

## Inputs and reproduction

The three electricity ZIPs were found locally, verified against all SHA-256
checksums in `config/data_sources.toml`, and extracted using `bootstrap_data.py`.
No identified data or raw telemetry is added to version control.

```bash
python scripts/run_baseline_audit.py
```

Windows and their interpretation are in `config/baseline_audit_windows.csv`.
Outputs under `outputs/generated/baseline_audit/`:

- `input_inventory.csv`: exact source filenames, checksums, valid endpoints,
  duplicate timestamps, and low-voltage counts.
- `daily_sensor_coverage.csv`: distinct observed/powered two-minute bins by day.
- `single_sensor_comparisons.csv`: inherited source windows, earlier candidate
  windows, both uptime denominators, calendar-window sensitivity, and PQR.
- `post_sensor_comparison.csv`: paired uptime and each constituent sensor alone
  over identical follow-up windows and exclusions.

## Reconstructed inherited comparisons

Uptime below uses median voltage in UTC-aligned two-minute bins and a powered
threshold strictly greater than 23 V. The monitoring denominator begins at the
first valid bin and ends at the last valid bin within the configured comparison.

| Facility | PowerWatch source window, actual valid endpoints (UTC) | Expected-window uptime | Uptime among observed bins | Observed-bin coverage |
|---|---|---:|---:|---:|
| CH1 | 3 Apr 2024 14:45:23 to 8 Jan 2025 04:06:04 | 69.154% | 75.145% | 92.027% |
| CSR2 | 4 Jul 2024 08:19:02 to 27 Jul 2024 23:58:04 | 14.339% | 30.148% | 47.560% |
| CSR4 | 4 Jan 2025 08:53:14 to 28 Jan 2025 23:16:03 | 72.828% | 80.979% | 89.934% |

CH1 and CSR4 closely approximate the inherited 69.2% and 72.8%. CSR2's inherited
14.9% is not exactly reproduced with the documented July window. Do not select
new endpoints simply to recover that value. The original uptime script/window
would be needed to resolve the difference.

These are SINGLE PowerWatch sensor calculations. Missing bins count against the
expected-window estimate, but remain unknown electrical states. The observed-bin
estimate excludes missing bins; it can overestimate service availability if
telemetry loss preferentially accompanies power loss.

The old notebook counted raw rows against elapsed-time expected samples.
The audit exposes that result separately: CH1 69.255%, CSR2 14.345%, CSR4
72.843%. Two-minute binning removes duplicate/bin-collision effects. Neither
legacy variant establishes a paired baseline.

## What is actually earlier?

- CH1-PW-02 has usable data from 3 April 2024. Restricting it to before the
  configured 30 April intervention-source monitoring start gives 39.020%
  expected-window uptime, 49.788% observed uptime, and 78.371% coverage. This
  cutoff is a monitoring/source date, not a verified commissioning date.
- CH1 HOP has only 58 valid minute records on three isolated dates before April
  (18 January, 14 March, 25 March); substantial reporting begins 26 May. Those
  isolated records cannot support a credible pre-installation uptime estimate.
  There are no valid HOP readings during 3–29 April.
- CSR2 HOP first reports on 22 May 2024; PowerWatch first reports on 28 May.
  No earlier observations are present in these supplied sensor files. The July
  old-solar window occurs after the documented broad deployment period.
- CSR4 HOP has 6,860 valid minute records from 19–25 March 2024. They are all
  above 23 V; two-minute observed-bin coverage is 83.026% between endpoints.
  The sensor is mapped to FLEX in the release, so its March power source must
  be established before using it as a baseline. There is no corresponding
  PowerWatch series before 27 May. This is roughly six days, not 25–28 days.

HOP is present during CSR2's July and CSR4's January source comparisons, but
the mapping associates it with the intervention circuit. Combining it with a
PowerWatch sensor described as old solar/grid would confuse different supplies
with redundant sensors on the same supply. No paired baseline is calculated.

## Paired follow-up and single-sensor sensitivity

These are co-source pairs from `config/paired_sensors.csv`, after applying
configured source starts and exclusions. Each single-sensor sensitivity uses
the SAME shared paired window, not its own longer observation span.

| Facility | Paired expected-window uptime | Paired observed uptime | HOP alone, expected-window | PowerWatch alone, expected-window | Both sensors observed |
|---|---:|---:|---:|---:|---:|
| CH1 | 99.091% | 99.842% | 96.821% | 74.251% | 74.623% |
| CSR2 | 99.263% | 99.574% | 96.358% | 82.949% | 84.939% |
| CSR4 | 99.797% | 99.819% | 97.586% | 98.888% | 97.174% |

Paired windows: CH1 25 May 2024–3 November 2025; CSR2 14 August 2024–25 November
2025; CSR4 12 August–5 December 2024. Exact UTC endpoints are in the CSV.
Two-sensor configuration does not mean both sensors reported in every interval.
The output therefore separates two-observed, one-observed, discordant,
both-missing, both-low, and single-observed-low intervals.

No HOP voltage at or below 23 V occurs in these three supplied files, and no
both-low paired bins are observed. This is not evidence of zero real outages:
HOP missingness may accompany loss of power. Bins with a low PowerWatch reading
and missing HOP remain single-sensor low-voltage evidence. Do not label them
double-confirmed outages; likewise do not label both-missing bins confirmed
electrical outages.

## Why the inherited voltage-quality values differ

The old notebook applied a JOINT voltage/frequency validity filter before
calculating either outcome. This reproduces the inherited voltage-quality
values: CH1 2.9296%, CSR2 1.3109%, CSR4 33.4783%.

The current library calculates voltage quality independently of frequency
validity. For the same source windows it gives CH1 23.6347%, CSR2 1.3099%,
CSR4 52.2012%. Missing/invalid frequency therefore previously removed many
otherwise valid voltage readings. Choose the denominator explicitly and apply
it consistently; the legacy values are not validated merely by reproducing them.
The audit includes frequency compliance at ±1%, ±5%, and ±10%.

## Figure 3 reporting decisions and remaining limits

1. CSR4's March HOP readings are excluded from the Figure 3 comparison because
   their source is unconfirmed. Their precise installation history therefore
   does not determine the regenerated figure.
2. The July CSR2 and January CSR4 windows are retained as documented existing-
   source comparisons. They are not labelled pre-installation observations.
   The study author confirmed these source assignments on 10 October 2026;
   source-status metadata records that confirmation. CH1's inherited long source window
   is also retained as a comparison rather than a strict pre-installation window.
3. The main comparable figure uses the inherited joint voltage/frequency-validity
   policy consistently for reconstructed comparisons AND follow-up. An independent-
   denominator sensitivity figure is supplied alongside it. Neither policy
   changes missingness into confirmed outage evidence.
4. Figure metadata and footnotes distinguish single PowerWatch comparisons,
   paired follow-up, and the three still-inherited longitudinal baselines.
5. The summary retains its original ±5% frequency threshold. The top trace band
   is corrected from unlabelled ±2% to labelled ±1%. Supplementary tables expose
   all three requested thresholds; missing longitudinal baseline ±1%/±10% values
   remain blank and must not be filled by relabelling ±5% values.

Suggested caption wording: “Existing-source
comparisons at CH1, CSR2, and CSR4 use a single PowerWatch sensor during the
specified source-specific windows. Intervention-circuit follow-up uses matched
HOP and PowerWatch sensors, with power recorded when either reports >23 V.
Sensor configurations and observation periods differ; these comparisons are
descriptive and are not matched pre-installation/post-installation estimates.”

`manuscript_pre_results.csv` is retained as a historical reference. The Figure 3
script replaces its CH1/CSR2/CSR4 inputs using the regenerated audit, and fails if
those inputs are absent rather than silently reverting to manuscript numbers.
This audit does not certify the other three facilities' longitudinal baselines.
