# Manuscript Results Claim Verification

This table is the control surface for aligning the repository to the current
manuscript Results section. “Verified” requires regenerated output, a fixed
estimand, reviewed inclusion windows, and documented exclusions.

| Manuscript claim or figure | Current evidence | Status | Remaining requirement |
|---|---|---|---|
| Protected critical circuits improved uptime after intervention | Seven paired circuits can be regenerated under two uptime denominators | Not yet verified | Exact pre/post windows, conflict exclusions, and denominator decision |
| Voltage compliance improved after intervention | Post-FLEX conditional voltage quality regenerates for seven paired sensors | Not yet verified | Rebuild comparable pre-intervention facility windows |
| Frequency compliance improved after intervention | Post-FLEX ±1% and ±10% metrics regenerate | Not yet verified | Rebuild pre-intervention metrics using identical rules |
| Most systems achieved near-continuous service | Observed-evidence uptime is approximately 96–99%; expected-window uptime ranges much lower when both sensors are missing | Definition-sensitive | Confirm whether dual-sensor missing intervals are excluded or treated as downtime |
| Intervention systems delivered 18.3 MWh | Current non-duplicative installed-system reconstruction is 18.21 MWh; core critical circuits are 17.36 MWh and supplemental morgues 0.85 MWh | Close but not verified | Identify third manuscript-referenced morgue system and reconcile active windows |
| Figure 3 top: CSR1 morgue pre/post time series | Relevant sensor mapping exists | Not started | Exact pre/post source and transition dates; reproduce voltage/frequency panel |
| Figure 3 bottom: facility pre/post uptime and quality distributions | Post metrics and uptime sensitivities exist | Not started | Complete pre metrics and define facility aggregation |
| Figure 5: cumulative monitored energy | Regenerated from nine non-duplicative HOP system meters with core/morgue separation | Provisional | Confirm topology and manuscript inclusion scope |

## Generated evidence locations

- `outputs/generated/reliability/manuscript_uptime_sensitivity.csv`
- `outputs/generated/power_quality/post_flex_conditional_quality_by_sensor.csv`
- `outputs/generated/power_quality/post_flex_conditional_quality_by_facility.csv`
- `outputs/generated/energy/total_consumption_by_facility.csv`
- `outputs/generated/energy/fleet_cumulative_energy.svg`

