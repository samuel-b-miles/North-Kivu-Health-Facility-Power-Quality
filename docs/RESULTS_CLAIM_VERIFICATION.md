# Manuscript Results Claim Verification

This table is the control surface for aligning the repository to the current
manuscript Results section. “Verified” requires regenerated output, a fixed
estimand, reviewed inclusion windows, and documented exclusions.

| Manuscript claim or figure | Current evidence | Status | Remaining requirement |
|---|---|---|---|
| Protected critical circuits improved uptime after intervention | Seven paired circuits regenerate using confirmed PowerWatch source dates and telemetry exclusions under two uptime denominators | Not yet verified | Comparable pre-intervention windows and denominator decision |
| Voltage compliance improved after intervention | Post-FLEX conditional voltage quality regenerates for seven paired sensors | Not yet verified | Rebuild comparable pre-intervention facility windows |
| Frequency compliance improved after intervention | Post-FLEX ±1% and ±10% metrics regenerate | Not yet verified | Rebuild pre-intervention metrics using identical rules |
| Most systems achieved near-continuous service | Current primary-facility expected-window uptime ranges from about 95.5–99.8%; observed-evidence uptime and missingness are reported separately | Definition-sensitive | Expected-window uptime is a conservative monitoring measure; do not equate both-missing intervals with confirmed outages |
| Intervention systems delivered 18.2 MWh | Current non-duplicative installed-system reconstruction is 18.21 MWh; core critical circuits are 17.36 MWh and supplemental morgues 0.85 MWh | Reproduced from included HOP meters | Continue to label known telemetry gaps when plotting consumption over time |
| Figure 3 top: CSR1 source comparison time series | Existing-grid and protected-circuit traces regenerate; frequency band explicitly ±1% | Reproduced from mapped sensors | Confirm commissioning annotation and clinical-load description; source map identifies the protected core circuit rather than a morgue-only circuit |
| Figure 3 bottom: facility source comparison distributions | CH1/CSR2/CSR4 source comparisons reconstructed; paired follow-up regenerated; joint-valid PQR and independent sensitivity supplied | Partially reproduced | Independently reconstruct HGR1/CSR1/CSR3 baselines; align manuscript terminology and frequency tolerances with selected figure |
| Figure 4: monthly monitored energy consumption | Regenerated from nine non-duplicative HOP system meters with core/morgue separation; panels ordered HGR1, CH1, CSR1, CSR2, CSR3, CSR4 | Provisional | Confirm topology and manuscript inclusion scope |

## Generated evidence locations

- `outputs/generated/reliability/manuscript_uptime_sensitivity.csv`
- `outputs/generated/power_quality/post_flex_conditional_quality_by_sensor.csv`
- `outputs/generated/power_quality/post_flex_conditional_quality_by_facility.csv`
- `outputs/generated/energy/total_consumption_by_facility.csv`
- `outputs/generated/energy/figure4_monthly_energy_six_panel.svg`
- `outputs/generated/energy/fleet_cumulative_energy.svg`
- `outputs/generated/figure3/pre_post_summary.csv`
- `outputs/generated/figure3/pre_post_summary.svg`
- `outputs/generated/baseline_audit/single_sensor_comparisons.csv`
- `outputs/generated/baseline_audit/post_sensor_comparison.csv`
- `publication/figure3/`
