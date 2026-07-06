# Uptime Methods and Primary Estimand

## Primary post-intervention uptime

The primary post-intervention uptime metric follows the manuscript language and
the combined-sensor table footnote:

1. Restrict to dates when PowerWatch is confirmed to monitor the intervention
   source.
2. Remove confirmed telemetry-exclusion periods.
3. Resample HOP and PowerWatch voltage to common two-minute bins using the median.
4. Restrict to the shared valid-data window: the later first valid observation
   through the earlier last valid observation.
5. Mark a bin powered when **either** sensor reports voltage above 23 V.
6. Divide powered bins by all expected two-minute bins in the shared window.

This means a bin with no powered reading—including when both sensors are
offline—counts against uptime. This is conservative and matches the statement
that an outage occurs when both matched sensors concurrently meet outage
conditions (`voltage <= 23 V` or offline).

## Required sensitivity analyses

- **Observed-evidence uptime:** same numerator, divided only by bins where at
  least one sensor reports voltage. This isolates electrical evidence from
  dual-sensor telemetry loss.
- **Concordant-pair availability:** uses only bins where both sensors agree on
  powered versus outage status. This is diagnostic, not the manuscript primary.

## Audit against draft post-intervention values

The primary method closely reproduces draft values for CSR2, CSR3 parallel
F1/F2, CSR1, and HGR1. Two draft values require correction:

- **CH1:** the 94.6% draft result comes from including PowerWatch observations
  before the confirmed intervention-source date. Restricting to post-source data
  and the shared valid window yields approximately 99.1%.
- **CSR4:** the 78.9% draft result used an obsolete, shorter conflict exclusion.
  With the confirmed 2024-12-06 to 2025-10-02 exclusion, paired post-FLEX uptime
  is estimated only in the valid pre-exclusion paired window and is approximately
  99.8%.

All pre-intervention values currently used in the summary figure are explicitly
marked manuscript-reported and pending independent reproduction.
