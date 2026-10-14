# Figure 2 — approved implementation and monitoring timeline

`figure2.svg` is the vector master; `figure2.png` is the 4500-pixel, 600-DPI
publication export (7.5 inches wide). The revised labels and MM/YYYY axes were
approved on 2026-10-14, with `(n = 6)` added to the payment and maintenance ledger.
The standalone Prospect energy-demand row is removed; paired Prospect and
GridWatch telemetry remains. All retained bar time boundaries are unchanged.

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
