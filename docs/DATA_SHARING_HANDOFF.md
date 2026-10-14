# Submission data-sharing handoff

Prepared 10 October 2026. This is a release inventory, not approval to publish new source data.

## Recommended public package

Publish analysis inputs sufficient to calculate the reported estimates, with dictionaries, configuration, code, and exact figure/table source values. A plotted summary alone cannot establish source-level reproducibility.

| Domain/output | Present public inputs | Reproduction status | Additional release candidate |
|---|---|---|---|
| Health Table 2 and descriptive dashboard | Ward-month and facility-month DHIS2 panels; ward and analysis configuration | Public analytical reproduction verified using `run_health.py --from-public` | Preserve reporting/imputation flags and dictionary; review small ward counts with partners |
| Figure 6 and financial tables | Coded payment ledger and CAPEX/commitment configuration | Public reproduction verified using `run_payments.py` | Versioned output tables and a payment field dictionary |
| Figure 3 summary and sensitivities | Exact comparison values, threshold tables, sensor comparisons, input hashes in `publication/figure3/` | Published values available; recomputation requires restricted telemetry | Two-minute analysis series with explicit observed/unknown/excluded states and sensor roles; original-resolution input when needed to reproduce preprocessing |
| Figure 3 time-series panel | Published SVG/PDF/PNG; code specifies sampling | Rendering from source requires restricted GridWatch exports | Exact plotted 20-minute series; distinguish display sampling from two-minute calculation inputs |
| Figure 4 and energy tables | Meter selections and exclusions | Requires restricted HOP daily-energy archive | Meter-day energy with active-window flags, circuit groups and missingness; avoid double-counted downstream loads |
| Reliability and power-quality annex | Sensor pairs, analysis windows, thresholds | Requires restricted HOP/GridWatch archives | Same analysis-series release as Figure 3, plus denominator and coverage tables |
| Timeline | Dates and labels embedded in plotting script | Public rendering possible | Machine-readable event table; source/date verification remains separate |

A public release candidate should omit facility-name crosswalks, original hardware identifiers, raw organisation-unit identifiers, free text and participant identifiers. Public facility codes, exact dates, rare events and small health counts can still permit inference. Treat the existing files as coded/deidentified, rather than claiming irreversible anonymity. Review disclosure risk and sharing authority with partners before adding telemetry or expanding health releases. Do not suppress or shift analytical values silently: document changes and their effect on reproduction. Preserve restricted original inputs for authorised verification.

## Access process confirmed by the corresponding author

Researchers should contact Samuel B. Miles through the corresponding-author contact in the manuscript, specifying the research purpose, requested datasets, intended analyses and institution. Requests for underlying data or supporting documents are considered case by case in consultation with study partners and relevant authorities, subject to applicable ethics approvals, consent provisions and data-sharing requirements. Where sharing is permitted, reasonable arrangements will support access while protecting confidentiality. This is not an unconditional promise that every requested file can be shared.

Before submission, supply the exact contact address, start date and access duration, and identify which supporting documents may be shared. Do not invent a response deadline or blanket approval. Record decisions and any data-use conditions. Public code availability does not establish a data reuse licence; choose code/data licences only when ownership and permissions are confirmed.

## Draft manuscript statement

Analysis code, coded analytical health-service panels, the coded payment ledger, and Figure 3 source tables are available at https://github.com/samuel-b-miles/North-Kivu-Health-Facility-Power-Quality. These public files support health-service and payment analyses and inspection of Figure 3 results; complete source-level electricity reproduction requires additional telemetry. Researchers may request underlying telemetry, other study data and supporting documentation from the corresponding author, describing the proposed purpose and data required. Access decisions will be made in consultation with study partners and relevant authorities, subject to applicable ethics approvals, consent provisions and data-sharing requirements. Where sharing is permitted, reasonable arrangements will be made to support access while protecting confidentiality.

Add confirmed availability dates/duration and a permanent archive DOI before treating this as the final submission statement.

## Public reproduction checked

```bash
pip install -e '.[dev]'
python scripts/run_health.py --from-public
python scripts/run_payments.py
python scripts/run_timeline_figure.py
```

The public health mode rebuilds the facility panel from the ward panel and calculates Table 2, descriptive summaries, completeness, missing-month and implausibility checks, and the dashboard. It does not overwrite public inputs or manufacture raw duplicate/mapping audits. Source cleaning remains a separate restricted workflow. `run_all.py --from-public` uses public health panels, but still requires the four telemetry archives. The complete candidate supplies these; source DHIS2 cleaning remains restricted.

## Evidence and limits of policy check

The Lancet Global Health author-signature form requires authors to agree to the manuscript's data-access statements: https://www.lancet.com/pb/assets/raw/Lancet/authors/tlgh-author-signatures.pdf.

ICMJE recommends methods detailed enough for others with the data to reproduce results: https://www.icmje.org/recommendations/browse/manuscript-preparation/preparing-for-submission.html. Its clinical-trial sharing framework specifies data, documents, timing and access criteria: https://www.icmje.org/news-and-editorials/data_sharing_june_2017.pdf. Use that framework to make this study's statement concrete; it does not establish that this observational implementation study must publish every raw record.

The current Global Health Information for Authors PDF could not be fetched (HTTP 403). Check the submission portal's current instructions before final submission. The public-package recommendation above is a reproducibility recommendation, not a verified journal mandate to open all raw data.
