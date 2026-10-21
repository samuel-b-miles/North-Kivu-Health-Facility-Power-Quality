# Table 1 approved editable source

`source.json` is the 2026-10-21 approved six-facility table, transcribed and
verified against Library DRC71_Table1_LGH_preview.docx version 2.
`scripts/build_submission_tables.py` renders its grouped equipment heading,
black/white horizontal rules, separate critical-circuit lines, Yes/No entries
and acronym definitions as vector PDF. The CSR3 row has no asterisk, and no
negotiated-fee footnote or caption is embedded. The caption stays in the prose
manuscript. Run `python scripts/build_submission_pdf.py` for the full build.

This is presentation source only; it does not override payment-analysis data.
