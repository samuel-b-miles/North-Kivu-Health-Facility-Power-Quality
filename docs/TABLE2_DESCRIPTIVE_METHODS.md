# Table 2: full-period descriptive mortality and conditional uncertainty

Table 2 summarizes January 2023-December 2025, all 36 calendar months, including
pre- and post-installation observations. Its purpose is reporting quality and
continuity. It estimates neither an intervention effect nor proof of group
comparability. It includes no exploratory treatment-by-period analysis.

The mortality point estimate remains the unweighted mean of observed
facility-month rates under the existing data-construction rules. Each
positive-admission facility-month contributes one observation, not each
patient and not each equally weighted hospital. There are 204 contributing
facility-month rates and six hospitals per arm. The means are unchanged:
1.6835884081% treatment and 1.5048579559% control.

## Important unresolved blank-death convention

The inherited notebook and `src/drc_power/dhis2.py` assign zero to each blank
death component before summing before-/after-48-hour deaths. Where both
components are blank, the public ward data retain an explicit imputation
flag. The source meaning of blanks has not been fully validated across these
data; sparse zero encoding must not be assumed to establish complete death
reporting. Missing admission observations remain missing, not zero.

Across the full period, 35 treatment and 44 control facility-month rates have
all contributing death components blank. These become zero mortality under
the inherited rule. Every included facility-month has at least one missing
death component in a contributing ward. Thus the intervals below are
conditional on the existing blank=zero convention. They do not incorporate
uncertainty or bias from source missingness, incomplete ward reporting, death
imputation or source transcription. Admission-completeness checks do not
validate death-field completeness. No data or point estimates were silently
changed for this presentation update.

## Hospital-cluster-robust Wald-type interval

For mortality percentages y_i with mean m, N rows and G contributing hospitals,
let S_g=sum_i(y_i-m) within hospital g. The intercept-only CR1 variance is:

V = [G/(G-1)] * sum_g(S_g^2) / N^2.

The usual (N-1)/(N-K) factor is 1 because K=1. The 95% interval is
m +/- t_(G-1,0.975) * sqrt(V). Here G=6, df=5 and t=2.5705818356. The software
computes the actual contributing cluster count, rather than hard-coding it.

| Arm | Mean, % | Cluster SE, percentage points | 95% CI, % |
|---|---:|---:|---:|
| Treatment | 1.683588 | 0.493106 | 0.416020 to 2.951156 |
| Control | 1.504858 | 0.277685 | 0.791045 to 2.218671 |

The displayed mortality row uses two decimals. The interval allows
within-hospital dependence under an independent-hospital working assumption;
coverage remains approximate with only six clusters per arm. Zero empirical
cluster variance is flagged as uninformative rather than evidence of no risk.
Symmetric bounds are not silently truncated. A normal-reference sensitivity
is exported separately and is not the primary interval.

These are descriptive confidence intervals, not treatment-effect tests or
patient-level binomial intervals. Overlap does not prove equality or
comparability. Missing-death assumptions and shared shocks are not repaired
by clustering. See Cameron and Miller, A Practitioner's Guide to
Cluster-Robust Inference:
https://cameron.econ.ucdavis.edu/research/Cameron_Miller_JHR_2015_February.pdf

## Reproduce the canonical deliverables

```bash
pip install -e '.[publication,figures,dev]'
python -m pytest -q
python scripts/build_submission_pdf.py
```

The health step writes `table2_mortality_cluster_intervals.csv` with the
estimate, SE, limits, N, G, degrees of freedom, critical value and method.
The submission build regenerates both consistently styled caption-free
4500-pixel table PNGs, their vector PDFs, approved Figure 2, and the eight-page
Figures 1-5/Tables 1-2 compilation. Source values and eligibility are unchanged.

GitHub Actions: **Submission figures and tables**,
`.github/workflows/submission-figures-tables.yml`. No manual inputs are
required. The artifact is `submission-figures-and-tables`; it contains the
compiled PDF, source/hash manifest, table exports and interval methods.
No private crosswalks, identified source extracts, scanned forms or exploratory
analyses belong to that artifact.
