#!/usr/bin/env python3
"""Export Figure 3 as SVG, 600-DPI PNG, and vector PDF; preserve its data/caption."""

import argparse
from io import BytesIO
from pathlib import Path
import shutil
import xml.etree.ElementTree as ET

from pipeline_common import DEFAULT_OUTPUT_ROOT, PROJECT_ROOT


CAPTION = """Figure 3. Electricity performance of existing supplies and protected intervention circuits.
Top: CSR1 existing micro-hydro and protected-circuit voltage/frequency traces.
Bottom: Facility trajectories for uptime, voltage compliance (207–253 V), and
frequency compliance (47.5–52.5 Hz; ±5%). CH1, CSR2, and CSR4 existing-source
comparisons are reconstructed from a single PowerWatch sensor over the documented
source windows, which are not uniformly pre-installation periods. HGR1, CSR1,
and CSR3 baseline values remain inherited and await independent reconstruction.
Protected-circuit uptime uses matched HOP and PowerWatch sensors and counts a
two-minute bin as powered when either reports >23 V. Missing bins count against
expected-window uptime but do not establish electrical outages; observed-evidence
uptime and sensor coverage are supplied separately. PQR in the main summary uses
jointly valid voltage/frequency observations in both reconstructed comparison and
follow-up periods, matching the inherited complete-case definition. Separate
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
    parser.add_argument("--dpi", type=int, default=600)
    args = parser.parse_args()
    import resvg_py
    from PIL import Image
    from svglib.svglib import svg2rlg
    from reportlab.graphics import renderPDF

    source = args.output_root / "figure3"
    release = args.release_dir
    release.mkdir(parents=True, exist_ok=True)
    names = [("csr1_pre_post_timeseries.svg", "figure3_timeseries.svg"),
             ("pre_post_summary.svg", "figure3_summary.svg"),
             ("source_comparison_independent_pqr.svg", "figure3_independent_pqr_sensitivity.svg")]
    for name, destination in names:
        shutil.copy2(source / name, release / destination)
    combine(release / "figure3_timeseries.svg", release / "figure3_summary.svg", release / "figure3.svg")
    for name in [destination for _, destination in names] + ["figure3.svg"]:
        svg = release / name
        png_bytes = resvg_py.svg_to_bytes(svg_path=str(svg), width=round(7.5 * args.dpi))
        with Image.open(BytesIO(png_bytes)) as img:
            img.save(svg.with_suffix(".png"), dpi=(args.dpi, args.dpi))
        drawing = svg2rlg(str(svg))
        pdf_scale = 7.5 * 72 / drawing.width
        drawing.scale(pdf_scale, pdf_scale)
        drawing.width *= pdf_scale
        drawing.height *= pdf_scale
        renderPDF.drawToFile(drawing, str(svg.with_suffix(".pdf")))
        # A compact preview keeps visual inspection independent of export size.
        (release / f"{svg.stem}_preview.png").write_bytes(
            resvg_py.svg_to_bytes(svg_path=str(svg), width=1650))
    for name in ["pre_post_summary.csv", "source_comparison_independent_pqr.csv",
                 "frequency_thresholds_joint.csv", "frequency_thresholds_independent.csv"]:
        shutil.copy2(source / name, release / name)
    for name in ["single_sensor_comparisons.csv", "post_sensor_comparison.csv", "input_inventory.csv"]:
        shutil.copy2(args.output_root / "baseline_audit" / name, release / name)
    (release / "caption.txt").write_text(CAPTION, encoding="utf-8")
    print(f"Figure 3 delivery: {release}")


if __name__ == "__main__":
    main()
