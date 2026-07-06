# Analysis Decision Log

## Confirmed decisions

### Separate reliability from conditional power quality

Voltage/frequency compliance is calculated only while usable voltage is
observed. Outages and missing telemetry are reported separately.

### Preserve missing telemetry as unknown

Primary reliability estimates do not convert missing sensor records into
outages. A separately named conservative sensitivity estimate may count unknown
intervals against availability.

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

## Pending decisions

- Exact intervention and conflict-exclusion dates.
- Include/exclude rationale for the CSR3 grid files marked `omitted`.
- Source or disposition of the missing CSR1 radiography PowerWatch file.
- Inclusion and anonymized identifier for the CH1 sterilizer HOP meter.
- Electrical topology required to avoid double-counting facility energy.
