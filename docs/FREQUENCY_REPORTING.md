# Four frequency intervals

All six facilities report ±0.1%, ±1%, ±5%, and ±10% of 50 Hz
(49.95–50.05, 49.5–50.5, 47.5–52.5, and 45–55 Hz, inclusive).
Frequency denominators retain voltage 23–400 V and frequency 30–70 Hz,
both inclusive. Missing or invalid readings are not zero compliance or outages.
Independent and joint policies have identical frequency denominators; their
voltage denominators can differ. Longitudinal baseline aggregation remains
equal sensor means in each selected window. CSR1 retains each sensor's available
pre-source records, rather than restricting to overlap. Follow-up remains pooled
valid readings across the configured source sensors, weighted by valid counts.

A local raw-input rerun on 2026-10-14 produced the following percentages.
Existing-source values are from the saved selected longitudinal baselines and
single-sensor inherited-source comparisons. Protected values were recomputed
from the canonical GridWatch CSVs with configured starts and exclusions.

| Facility | Existing ±0.1/1/5/10 (%) | Protected ±0.1/1/5/10 (%) | Protected valid readings |
|---|---|---|---:|
| HGR1 | 3.61 / 34.55 / 94.84 / 98.49 | 68.24 / 83.44 / 98.20 / 99.76 | 396431 |
| CH1 | 0.00 / 0.01 / 0.09 / 89.35 | 91.58 / 99.97 / 100.00 / 100.00 | 298862 |
| CSR1 | 0.45 / 2.56 / 12.28 / 29.59 | 93.92 / 99.47 / 100.00 / 100.00 | 142975 |
| CSR2 | 0.00 / 0.00 / 0.00 / 91.85 | 91.39 / 99.95 / 99.96 / 99.96 | 206784 |
| CSR3 | 11.16 / 77.38 / 82.08 / 85.94 | 93.52 / 99.89 / 100.00 / 100.00 | 241985 |
| CSR4 | 0.12 / 1.10 / 4.61 / 9.39 | 92.40 / 99.94 / 99.99 / 99.99 | 147065 |

Protected frequency record spans (UTC; gaps remain missing): HGR1 April 5, 2024–January 12, 2026;
CH1 April 30, 2024–November 3, 2025; CSR1 May 27–December 20, 2024;
CSR2 August 14, 2024–December 11, 2025; CSR3 May 27, 2024–July 9, 2025
(two sensors; one ends February 28, 2025); CSR4 August 12, 2024–January 12, 2026.
CSR4 excludes December 6, 2024–October 2, 2025 inclusively and uses the full
available frequency window, separate from the shorter paired uptime window.
The unverified CSR4 ±0.1% value 93.37% is superseded by 92.40%.

`publication/figure3/frequency_thresholds_joint.csv` and
`frequency_thresholds_independent.csv` retain unrounded results.
`protected_frequency_provenance.csv` supplies exact retained record bounds,
counts and aggregation without raw telemetry or private identifiers.

Reproduce with authorized extracted inputs and existing baseline/reliability outputs:

```sh
PYTHONPATH=src python scripts/run_power_quality.py --raw-root /path/to/authorized/extracted --output-root outputs/generated
PYTHONPATH=src python scripts/run_figure3_summary.py --pqr-policy joint
PYTHONPATH=src python scripts/run_figure3_summary.py --pqr-policy independent
python -m pytest -q
```

The rerun preserved every existing facility power-quality column and every
±1/5/10 threshold-export value. Regression tests cover four-threshold propagation,
numeric 0.1 export, valid denominator boundaries, unequal sensor counts, missing
frequency, and CSR4's inclusive exclusion with late records retained.
