# Longitudinal pre-intervention audit

HGR1, CSR1 and CSR3 now have reconstructed two-PowerWatch baselines. These
replace historical transcriptions in the submission figure; the alternatives
below explain window selection and sensor coverage. See `FIGURE3_DELIVERY.md`
for the selected six-facility results. Original unpublished extraction rules
are not assumed to be reproduced merely because the new values are close.

Run `python scripts/run_longitudinal_pre_audit.py` after importing telemetry.
The configured cutoffs in `config/longitudinal_pre_windows.csv` use the existing
intervention-source monitoring starts. These are reproducible candidate pre
windows, not independently verified installation dates or inherited extraction
dates. Outputs are `longitudinal_pre_comparisons.csv` and
`longitudinal_pre_inventory.csv` under `outputs/generated/baseline_audit/`.
The inventory records file hashes and row counts.

## Results from the available files

| Facility | Sensor basis | Expected-window uptime | Observed uptime | Joint-valid voltage quality | Frequency ±1% | Frequency ±5% | Frequency ±10% |
|---|---|---:|---:|---:|---:|---:|---:|
| HGR1 | PW-01, before configured start | 98.83% | 98.92% | 99.38% | 34.62% | 94.85% | 98.49% |
| HGR1 | PW-02, before configured start | 97.36% | 98.02% | 98.95% | 34.49% | 94.83% | 98.50% |
| HGR1 | Two sensors, shared overlap | 99.06% | 99.06% | 99.17% | 34.55% | 94.84% | 98.49% |
| CSR1 | Available PW-02, before configured start | 74.71% | 75.38% | 12.84% | 2.67% | 12.40% | 29.74% |
| CSR3 | PW-01, before configured start | 47.76% | 93.52% | 5.36% | 77.13% | 82.00% | 85.92% |
| CSR3 | PW-02, before configured start | 92.28% | 94.74% | 5.13% | 77.67% | 82.19% | 85.98% |
| CSR3 | Two sensors, shared overlap | 95.74% | 95.97% | 5.18% | 77.38% | 82.08% | 85.94% |

Single-sensor full pre windows and paired overlap windows differ. The exported
table additionally supplies each sensor over exactly the paired window. Paired
quality is an equal-weight sensor mean within that shared window. Paired uptime
counts a bin as powered if either sensor is above 23 V; pairing remains a
sensitivity pending confirmation of common supply and measurement topology.
Missing bins remain explicit; expected-window uptime is a conservative
powered-bin fraction, not an estimate that all missing bins were outages.

## Historical discrepancies and selected replacements

- HGR1 inherited values are 97.9% uptime, 99.1% voltage and 95.3% frequency
  (±5%). The selected shared pre-source window gives 99.06%, 99.17% and
  94.84%, replacing rather than assuming the old window and aggregation rule. The inherited PRE site summary extends
  to April 11, 2024, beyond the configured April 5 intervention-source start.
- CSR1 inherited values are 44%, 12% and 12%. Available PW-02 supports similar
  quality but does not reproduce 44% uptime. The documented PW-01 is absent
  from the original pilot release but now recovered from a verified DRC1
  workbook (see `DRC1_BASELINE_SUPPLEMENT.md`). The inherited PRE summary uses PW-02 through
  December 2024 and therefore is not a pure pre-intervention extraction.
- CSR3 inherited values are 95%, 5% and 82%. Available files closely reproduce
  quality. PW-02 ends July 12, 2023; PW-01 continues into July 2024 but has
  substantial missingness. The paired overlap ends July 2023. The files are
  marked `omitted` in the export. Verified existing-grid identities support
  their configured baseline-only use; the label is preserved and later dropout
  is exposed in the full-record sensitivity rather than ignored.

The study team's DRC1 anonymized Drive dataset is an additional source. Its
facility-code namespace differs from this pilot's namespace; join only using a
private verified crosswalk, never code equality alone. Its 1,770,531,676-byte
CSV could not be fetched through the connector's 268,435,456-byte limit, even
using the raw streamed-file option. Individual DRC1 workbooks were subsequently
retrieved and audited: the laboratory series matches the pilot's PW-02 and the
second baseline series supplies PW-01. See `DRC1_BASELINE_SUPPLEMENT.md`.

Retain ±5% as the main frequency threshold as selected by the study team;
±1%/±10% alternatives are now calculated for the available candidate windows.
No new paired estimate is certified as the inherited calculation.

## Study-team decision and identity verification

The study team accepts replacing the inherited 44% estimate with a reproducible
estimate around 74%, subject to checking the available second baseline sensor.
Do not describe the site's deployment as single-sensor merely because the
original release contains one input series. The 74.71% calculation above uses
one series. Adding the recovered second series produces 74.81% expected-window
uptime over all available pre observations, with variable sensor coverage;
the shared-overlap sensitivity is 75.17%.

The private crosswalk was checked after an erroneous exchange of CSR1/CSR3
facility names in conversational reporting. The numerical audit and coded
tables above were not swapped. Use the verified private crosswalk for named
manuscript reporting, not the earlier conversational assignment. CSR3 has two
baseline files and is the site with inherited 95% uptime. CSR1 is the site with
inherited 44% uptime and an absent second file in the pilot release.

An alternative DRC1 source was located in the original project's per-device
two-minute-data folder. Individual Excel files are below the connector limit.
Deployment records identify two baseline devices at each of these sites.
Both CSR1 baseline workbooks have now been checked against the private device
crosswalk. All 583,782 laboratory timestamps match pilot PW-02; voltage and
frequency agree within 1e-9. The second sensor's 405,754 rows were projected
with full readback verification into a coded local supplement. This confirms
two contributing sensor files, not two-sensor coverage at every time point.
