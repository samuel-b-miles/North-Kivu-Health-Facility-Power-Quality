# Next Session: Align the Repository to the Manuscript Results

Start here. The analytical destination is the current manuscript Results
section, especially “Reliability and System Performance,” Figure 3, and Figure 5.

## Manuscript claims to reproduce

1. Protected critical circuits improved uptime, voltage compliance, and
   frequency compliance after intervention deployment.
2. Most systems achieved near-continuous service.
3. Installed intervention systems delivered approximately 18.3 MWh over about
   18 months.
4. Figure 3 compares pre/post uptime and power quality and includes a CSR1
   morgue time-series example.
5. Figure 5 shows cumulative monitored energy consumption.

## Estimands that must match the manuscript

- **Uptime:** proportion of monitored time when at least one sensor reported
  voltage above 23 V (10% of nominal). This is not the same as the current
  concordant-pair-only prototype and must be implemented explicitly.
- **Voltage quality:** within ±10% of 230 V while power is present.
- **Frequency quality:** manuscript reports ±1% and ±10% of 50 Hz. Do not center
  the main result on ±5% merely because an earlier notebook did so.
- **Energy:** distinguish core critical-circuit systems from supplemental morgue
  systems; exclude downstream equipment meters that double-count source energy.
- **Conflict exclusions:** apply exact uninstallation periods before denominators
  are calculated.

## Immediate workflow

1. Resolve the blocking questions in `QUESTIONS_FOR_ANTOINE.md`.
2. Replace provisional calendar-month exclusions with exact timestamps.
3. Implement the manuscript uptime definition and compare it with conservative
   and concordant-pair sensitivity analyses.
4. Rebuild Figure 3 from explicit pre/post facility windows.
5. Rebuild Figure 5 with separate critical-core and supplemental-morgue layers.
6. Reconcile the energy headline: excluding the CSR3 sterilizer produces about
   18.21 MWh from currently mapped systems, which rounds to 18.2 rather than the
   manuscript’s 18.3 MWh.
7. Generate a manuscript-claim verification table linking each sentence to its
   code, inputs, output, and final value.

## Decisions already made

- Updated PowerWatch exports are exact supersets of original exports.
- CSR3 sterilizer energy is excluded to prevent double counting.
- CSR1 and CSR3 morgue systems are reported separately from core critical circuits.
- Actual facility names and hardware identifiers remain outside tracked files.
