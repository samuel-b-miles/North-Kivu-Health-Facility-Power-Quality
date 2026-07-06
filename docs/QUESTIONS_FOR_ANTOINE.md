# Questions for Antoine

These are ordered by how directly they block defensible regeneration of the
headline outcomes.

## Blocking questions

1. **Confirmed-outage implementation:** Can you share
   `combined_uptime_analysis_v2.py`, or describe the exact two-minute alignment,
   outage threshold, tolerance, and treatment of discordant/missing pairs?
2. **Pre-intervention extraction:** Can you share
   `pre_intervention_pqr_extraction.py` and the exact start/end timestamps used
   for every facility—not only CSR2 and CSR4?
3. **Missing CSR1 grid sensor:** Was the public file corresponding to
   `CSR1-PW-01` intentionally withheld, accidentally omitted, or replaced by
   another baseline source?
4. **CSR3 omitted files:** Why are `CSR3-PW-01` and `CSR3-PW-02` marked
   `omitted`? Should either be used for baseline PQR, reliability, or neither?

## Important methodological questions

6. Which result table is the authoritative paired-sensor uptime output? It is
   referenced in documentation but absent from the release.
7. Why do current post-intervention PQR results contain nine sensors when prior
   notes describe eleven?
8. Were site-level PQR values intended as an unweighted mean of sensor
   percentages, a pooled observation-level estimate, or another estimand?
9. Does “voltage below 23 V” represent an outage to be excluded from conditional
   PQR, or a poor-quality observation in any manuscript table?
10. What exact electrification/commissioning date applies to every FLEX system?

## Energy questions

11. Is the legacy CH1 sterilizer meter part of the intervention
    evaluation, and what public anonymized identifier should it receive?
12. Please confirm that the CSR3 sterilizer meter is downstream of the parallel
    F1/F2 meter and should be excluded from system-level consumption totals.
13. Are daily-energy zeros true zero-use days, pre-installation padding, or
    missing telemetry encoded as zero?
14. Was `02_energy_generation_consumption.ipynb` intentionally excluded, and
    can you share the final version and its Prospect-meter inputs?

## Reproducibility and publication

15. Which checked-in outputs should be treated as manuscript-authoritative?
16. What software/environment generated the release results?
17. What license, citation, author order, and contribution statement should the
    public repository carry?

18. The manuscript states that three facilities added morgue-dedicated systems,
    while the released HOP mapping identifies morgue meters at CSR1 and CSR3.
    Which third morgue system is referenced, and is its energy meter in the release?

## Resolved with study-team context

- PowerWatch intervention-source dates are recorded for all six facilities in
  `config/analysis_periods.csv`.
- CSR4’s primary telemetry exclusion is 2024-12-06 through 2025-10-02.
- CSR1’s open-ended connectivity exclusion begins 2024-12-21.
- HOP coverage during these periods is documented in
  `docs/TELEMETRY_COVERAGE_AUDIT.md`.
