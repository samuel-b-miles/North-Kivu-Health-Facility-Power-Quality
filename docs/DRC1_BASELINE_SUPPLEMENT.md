# DRC1 baseline supplement for pilot CSR1

Two baseline PowerWatch devices are confirmed in the source deployment records.
The DRC1 and pilot facility codes use different namespaces. The verified
name/device crosswalk remains private; public files use pilot sensor codes.

## Accessible observations

| Coded sensor and source | Rows | First observation (UTC) | Last observation (UTC) |
|---|---:|---|---|
| CSR1-PW-01, recovered DRC1 workbook | 405,754 | 2022-06-28 09:04:06 | 2024-08-12 19:22:03 |
| CSR1-PW-02, DRC1 workbook | 583,782 | 2022-06-28 08:56:06 | 2024-10-15 23:58:06 |
| CSR1-PW-02, original pilot release | 625,366 | 2022-06-28 08:56:06 | 2024-12-21 05:40:04 |
| CSR1-PW-03, intervention-source pilot release | 146,304 | 2024-05-27 20:32:06 | 2024-12-21 05:42:14 |

All 583,782 DRC1 PW-02 timestamps match the pilot PW-02 timestamps, with no
voltage/frequency disagreement at tolerance 1e-9. They are overlapping versions
of the same sensor record, not independent sensors to pool. The pilot adds
41,584 readings. PW-01 has 405,719 readings before May 27, 2024, ending
February 9, 2024 at 14:38:06 UTC. Its remaining 35 readings are August 10–12,
2024 and must not be used as pre-intervention observations.

The pilot also supplies CSR1-HOP-01 from May 22 to December 20, 2024 and
CSR1-HOP-02 from October 15 to December 18, 2024. These are intervention/morgue
measurement streams, not substitutes for a missing longitudinal grid baseline.
File availability does not certify continuous coverage or device clock timezone.

## Reconstructed uptime

The candidate cutoff is the configured intervention-source start, May 27, 2024.
It is not an independently verified installation date. Two-minute median bins
are powered when either contributing sensor exceeds 23 V; missing bins are
reported separately. Common-supply/branch interpretation still requires the
study team's topology verification before interpreting facility-wide outages.

| Window | Expected-window uptime | Observed uptime | At least one sensor observed | Both sensors observed |
|---|---:|---:|---:|---:|
| All available pre readings, June 28, 2022–May 14, 2024 | 74.80575% | 75.38893% | 99.22644% | 81.94606% |
| Shared sensor overlap, June 28, 2022–February 9, 2024 | 75.16514% | 75.41885% | 99.66360% | 95.13634% |

Recommended reporting is **two sensors, with variable coverage**, accompanied
by the coverage percentages. The shared-overlap estimate is a sensitivity.
Neither estimate should be labelled single-sensor or continuously double-sensor.
Expected-window uptime is the fraction of expected bins with recorded powered
evidence; it does not establish that unobserved bins were outages.

The DRC1 Git repository at commit
`e19c48346079b8f5b8ada3e8e28572e9c28f2e3e` contains only
`Applied Energy Calculations and Figures.py`, without its required input data,
README or license. Lines 161–163 derive uptime from mean SAIFI multiplied by
median non-zero SAIDI, rather than a powered-interval fraction. This is a
different calculation and a possible explanation for inherited discrepancies;
the original 44% value has not been independently reproduced. The repository's
file paths and filenames alone do not establish observation dates.

## Local reproducible release candidate

`outputs/release_candidate/drc1-csr1-supplement-v1/` contains the complete second
sensor record as `CSR1-PW-01_CSR1_2min_og.csv` and a checksum manifest. The
allowlist retains only `time`, `voltage`, `frequency`, preserving row order,
measurement values and gaps. Site names, hardware IDs, coordinates and source
sheet labels are excluded. Full projection readback passed for all 405,754 rows.
Raw timestamps remain linkable; this is a deidentified release candidate, not
a claim that reidentification is impossible or that publication is approved.

Source workbook SHA-256:
`e80a2703a26c23ed9d3c68237259303ef4f98fc1c68bd03a1fe39d8c226cc13b`.

Coded CSV SHA-256:
`f5983571bd8735ea83cf3ff3548de106c167b25d35e9b3fe5072c82fba52f7b2`.

Reproduce using the existing approved telemetry and the supplement:

```sh
python scripts/run_longitudinal_pre_audit.py \
  --raw-root data/raw/extracted \
  --supplement-root outputs/release_candidate/drc1-csr1-supplement-v1 \
  --output-root outputs/generated/longitudinal_pre_with_drc1
```

The optional supplement leaves the original release inputs intact. Outputs
identify source basis, hashes, sensor counts, exact windows, coverage and
single/shared/union estimates. To prepare the supplement again from the private
source workbook, install the `data-import` extra and run
`scripts/prepare_powerwatch_workbook.py --help`. That script verifies the source
checksum, enforces the measurement allowlist and checks every exported row.

The earlier complete-v1 package does not contain this supplement or audit
update. A revised package must include the supplement, current scripts and
config, regenerate reference outputs and refresh manifests before publication.
Figure 3 now uses the selected two-sensor CSR1 full-record baseline. See
`FIGURE3_DELIVERY.md` for the complete six-facility audit.
