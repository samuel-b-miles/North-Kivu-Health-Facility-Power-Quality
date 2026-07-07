# DHIS2 Reproducibility Notes

Run `python scripts/run_health.py` after placing the authorized admissions and
deaths exports in `data/raw/dhis2/`. The script rebuilds both anonymized public
panels, QA reports, Table 2, descriptive pre/post summaries, and the HGR1
dashboard.

Important analytical decisions:

1. The primary window is January 2023 through December 2025; 2026 records are excluded.
2. Later `.1` columns take precedence over base columns after explicit conflict auditing. In the supplied exports, base and duplicate columns are complementary and have zero conflicts.
3. Facility-month outcomes aggregate only wards with reported admissions.
4. Missing death components contribute zero, matching the canonical notebook, but are flagged explicitly in public data.
5. Ward-month mortality observations with fewer than five admissions are excluded from primary ward-level summaries but retained publicly with a flag.
6. Main health results are descriptive and establish data feasibility, not causal effects.
