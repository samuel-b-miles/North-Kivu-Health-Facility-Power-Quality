# Analysis Decision Log

## Confirmed decisions

### Separate reliability from conditional power quality

Voltage/frequency compliance is calculated only while usable voltage is
observed. Outages and missing telemetry are reported separately.

### Preserve missing telemetry as unknown

Electrical evidence does not convert missing records into confirmed outages.
The manuscript primary is the conservative powered-bin fraction of expected
intervals; observed-evidence uptime and unknown bins are reported separately.

### Use updated PowerWatch exports for seven overlapping sensors

Record-level comparison found that every updated file is an exact superset of
its original: 2,999,567 overlapping timestamps with zero voltage or frequency
conflicts. See the canonical audit output for pair-level counts.

### Keep private identity data outside Git

Actual facility names and original hardware identifiers belong in a local-only
private mapping. All code, configurations, results, and logs use anonymized IDs.

### Exclude the CSR3 sterilizer meter from system-level consumption

The sterilizer is a downstream load supplied by the parallel FLEX F1/F2 system.
Adding its HOP total to the producing FLEX circuit would double-count energy.

### Separate morgue systems from the critical-circuit estimand

CSR1 and CSR3 morgue FLEX systems are intervention-funded installed systems but
are not part of the clinically critical-circuit estimand. Energy outputs report
core critical-circuit and supplemental morgue consumption separately.

### Use source-specific sensor coverage for telemetry estimands

Paired uptime and PowerWatch power-quality analyses are restricted to periods
when PowerWatch is known to monitor the intervention circuit. HOP energy totals
use their own active reporting periods and are not truncated to the later
PowerWatch source-switch date. Telemetry analyses do not claim to measure the
full period of system use when connectivity or source assignment is absent.
Payment and operations records will be analyzed separately as evidence of
service functionality and facility use.

## Pending decisions

- Exact intervention and conflict-exclusion dates.
- Original export rationale for the CSR3 `omitted` filename label; verified
  baseline-only use is now configured and dropout sensitivities are supplied.
- The original legacy 44% extraction/formula, if historical reconciliation is
  needed. The missing radiography series is recovered and the selected baseline
  is reconstructed from two contributing sensors.
- Inclusion and anonymized identifier for the CH1 sterilizer HOP meter.
- Electrical topology required to avoid double-counting facility energy.

## Six-facility baseline revision

All six historical Figure 3 baselines are replaced by source reconstructions. HGR1/CSR3 use shared pre-source overlap; CSR1 uses the full available pre record with variable two-sensor coverage. CH1/CSR2/CSR4 remain single-PowerWatch existing-source comparisons. ±5% remains primary and ±1%/±10% tables are complete. Historical values are retained solely for the audit trail. See FIGURE3_DELIVERY.md for exact windows, rationale and manuscript methods.
