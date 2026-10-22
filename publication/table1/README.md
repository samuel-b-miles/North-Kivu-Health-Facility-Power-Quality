# Table 1 approved editable source

`source.json` is the 2026-10-21 approved six-facility table, transcribed and
verified against Library DRC71_Table1_LGH_preview.docx version 2.
`scripts/build_submission_tables.py` renders its grouped equipment heading,
black/white horizontal rules, separate critical-circuit lines, Yes/No entries
and acronym definitions as vector PDF. The CSR3 row has no asterisk, and no
negotiated-fee footnote or caption is embedded. The caption stays in the prose
manuscript. Run `python scripts/build_submission_pdf.py` for the full build.

This is presentation source only; it does not override payment-analysis data.

## Consistent caption-free table exports (2026-10-22)

Both tables share Helvetica 12 pt body, Helvetica Bold 10.5 pt headers,
10.5 pt notes, 540 pt content width, 9 pt vertical and 4 pt horizontal cell
padding, black text and matching horizontal rules. At a 6.5-inch inserted
image width, body text is approximately 10 pt. The table source remains
editable; captions are supplied separately, never embedded in table PNGs.
`python scripts/export_submission_tables.py` writes both 4500-pixel-wide,
600-DPI PNGs from the vector PDFs; the full submission build calls it too.
