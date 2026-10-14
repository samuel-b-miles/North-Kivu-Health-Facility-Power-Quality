# Figure 2 — approved implementation and monitoring timeline

`figure2.svg` is the vector master; `figure2.png` is the 4500-pixel, 600-DPI
publication export (7.5 inches wide). The revised labels and MM/YYYY axes were
approved on 2026-10-14, with `(n = 6)` added to the payment and maintenance ledger.
The standalone Prospect energy-demand row is removed; paired Prospect and
GridWatch telemetry remains. The two grouped existing-supply bars now show the selected overall calendar-date
envelopes: longitudinal (n=3), 2022-06-22–2024-05-14; short monitoring
(n=3)*, 2024-04-03–2025-01-28. These combine differing facility windows.
Only the short-monitoring label carries an asterisk; its explanation is left
for the manuscript caption. All other row definitions are unchanged.
This alignment was approved on 2026-10-14.

Regenerate the SVG with:

```sh
python scripts/run_timeline_figure.py
```

The SVG is written to `outputs/generated/timeline/`. For a raster export using
the existing Cairo exporter, install the figures extra and run:

```sh
python scripts/export_timeline_figure.py --dpi 600 --width-inches 7.5
```

The uploaded complete-v3-four-frequency-intervals Zenodo review ZIP remains a
snapshot of commit 61b8a328 and predates this approved Figure 2 revision. Its
telemetry, payment, health and frequency results are unchanged. Rebuild the
release package in a later approved update if the revised figure should be included.

`figure2_manuscript.png` contains the same figure pixels, centered on a white
canvas matching the main manuscript's existing image aspect ratio. This avoids
cropping labels when replacing its anchored image object and preserves the
existing image box and caption layout.
