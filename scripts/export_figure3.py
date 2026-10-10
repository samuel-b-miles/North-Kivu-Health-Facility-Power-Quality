#!/usr/bin/env python3
"""Export Figure 3 as SVG, 3600-DPI PNG, and vector PDF; preserve its data/caption."""

import argparse
from pathlib import Path
import shutil
import xml.etree.ElementTree as ET

from pipeline_common import DEFAULT_OUTPUT_ROOT, PROJECT_ROOT
from export_timeline_figure import set_png_dpi


CAPTION = """Figure 3. Electricity performance of existing supplies and protected intervention circuits.
Top: CSR1 existing micro-hydro and protected-circuit voltage/frequency traces.
Bottom: Facility trajectories for uptime, voltage compliance (207–253 V), and
frequency compliance (47.5–52.5 Hz; ±5%). CH1, CSR2, and CSR4 existing-source
comparisons are reconstructed from a single PowerWatch sensor over the documented
source windows, which are not uniformly pre-installation periods. HGR1 and CSR3
use reconstructed two-PowerWatch shared pre-source windows; CSR1 uses the full
available pre-source window with two sensors and variable coverage, including
the recovered DRC1 series. Alternatives and individual-sensor results are supplied.
Cutoffs are configured intervention-source monitoring starts, not independently
verified installation dates.
Protected-circuit uptime uses matched HOP and PowerWatch sensors and counts a
two-minute bin as powered when either reports >23 V. Missing bins count against
expected-window uptime but do not establish electrical outages; observed-evidence
uptime and sensor coverage are supplied separately. PQR in the main summary uses
jointly valid voltage/frequency observations in both reconstructed comparison and
follow-up periods. Longitudinal baseline PQR is an equal sensor mean within
the selected window; follow-up PQR pools source-sensor observations. Separate
voltage/frequency denominators are supplied as a sensitivity figure. Time windows,
sensor basis, and source-history limitations are documented in BASELINE_RECONSTRUCTION.md.
The time-series frequency band is ±1%, matching its annotation; the summary
frequency panel retains ±5%. These tolerances must be distinguished in the manuscript.
"""


def combine(top: Path, bottom: Path, target: Path) -> None:
    ET.register_namespace("", "http://www.w3.org/2000/svg")
    roots = [ET.parse(p).getroot() for p in (top, bottom)]
    width = float(roots[0].get("width"))
    top_height = float(roots[0].get("height"))
    scale = width / float(roots[1].get("width"))
    gap = 35
    height = top_height + gap + float(roots[1].get("height")) * scale
    root = ET.Element("{http://www.w3.org/2000/svg}svg", {
        "width": str(int(width)), "height": str(int(height)),
        "viewBox": f"0 0 {width} {height}"})
    for i, source in enumerate(roots):
        transform = "translate(0 0)" if i == 0 else f"translate(0 {top_height+gap}) scale({scale})"
        group = ET.SubElement(root, "{http://www.w3.org/2000/svg}g", {"transform": transform})
        for child in source:
            group.append(child)
    ET.ElementTree(root).write(target, encoding="utf-8", xml_declaration=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument("--release-dir", type=Path, default=PROJECT_ROOT / "publication" / "figure3")
    parser.add_argument("--dpi", type=int, default=3600)
    parser.add_argument("--from-publication", action="store_true",
                        help="Render committed audited SVG masters without restricted raw inputs.")
    args = parser.parse_args()
    import resvg_py
    from svglib.svglib import svg2rlg
    from reportlab.graphics import renderPDF

    source = args.output_root / "figure3"
    release = args.release_dir
    release.mkdir(parents=True, exist_ok=True)
    names = [("csr1_pre_post_timeseries.svg", "figure3_timeseries.svg"),
             ("pre_post_summary.svg", "figure3_summary.svg"),
             ("source_comparison_independent_pqr.svg", "figure3_independent_pqr_sensitivity.svg")]
    for name, destination in names:
        master = PROJECT_ROOT / "publication" / "figure3" / destination if args.from_publication else source / name
        if master.resolve() != (release / destination).resolve():
            shutil.copy2(master, release / destination)
    combine(release / "figure3_timeseries.svg", release / "figure3_summary.svg", release / "figure3.svg")
    for name in [destination for _, destination in names] + ["figure3.svg"]:
        svg = release / name
        png_bytes = resvg_py.svg_to_bytes(svg_path=str(svg), width=round(7.5 * args.dpi))
        svg.with_suffix(".png").write_bytes(png_bytes)
        set_png_dpi(svg.with_suffix(".png"), args.dpi)
        del png_bytes
        drawing = svg2rlg(str(svg))
        pdf_scale = 7.5 * 72 / drawing.width
        drawing.scale(pdf_scale, pdf_scale)
        drawing.width *= pdf_scale
        drawing.height *= pdf_scale
        renderPDF.drawToFile(drawing, str(svg.with_suffix(".pdf")))
        # A compact preview keeps visual inspection independent of export size.
        (release / f"{svg.stem}_preview.png").write_bytes(
            resvg_py.svg_to_bytes(svg_path=str(svg), width=1650))
    if args.from_publication:
        for item in (PROJECT_ROOT / "publication" / "figure3").iterdir():
            if item.suffix in {".csv", ".txt"} and item.resolve() != (release / item.name).resolve():
                shutil.copy2(item, release / item.name)
        print(f"Figure 3 delivery: {release}")
        return
    for name in ["pre_post_summary.csv", "source_comparison_independent_pqr.csv",
                 "frequency_thresholds_joint.csv", "frequency_thresholds_independent.csv", "baseline_value_audit.csv"]:
        shutil.copy2(source / name, release / name)
    for name in ["single_sensor_comparisons.csv", "post_sensor_comparison.csv", "input_inventory.csv",
                 "longitudinal_pre_comparisons.csv", "selected_longitudinal_baselines.csv", "longitudinal_pre_inventory.csv"]:
        shutil.copy2(args.output_root / "baseline_audit" / name, release / name)
    (release / "caption.txt").write_text(CAPTION, encoding="utf-8")
    print(f"Figure 3 delivery: {release}")


if __name__ == "__main__":
    main()
