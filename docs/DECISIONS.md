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

## Pending decisions

- Exact intervention and conflict-exclusion dates.
- Include/exclude rationale for the CSR3 grid files marked `omitted`.
- Source or disposition of the missing CSR1 radiography PowerWatch file.
- Inclusion and anonymized identifier for the CH1 sterilizer HOP meter.
- Electrical topology required to avoid double-counting facility energy.
