#!/usr/bin/env python3
"""Regenerate analysis figures and assemble one large-format vector PDF.

The default command uses the public DHIS2 panels and locally installed,
checksum-verified telemetry. It leaves publication/figure3 untouched.
"""

from __future__ import annotations

import argparse
from hashlib import sha256
from io import BytesIO
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

from pypdf import PdfReader, PdfWriter, Transformation
from reportlab.pdfgen import canvas


ROOT = Path(__file__).resolve().parents[1]
GENERATED = ROOT / "outputs" / "generated"
DEFAULT_PDF = GENERATED / "figure_book" / "all_code_generated_figures_large.pdf"
MAIN_FIGURES = [
    ("Figure 1", ROOT / "publication/figure1/figure1_full_frames.pdf"),
    ("Figure 2", GENERATED / "timeline/figure_implementation_monitoring_timeline.svg"),
    ("Figure 3", GENERATED / "figure3/csr1_pre_post_timeseries.svg"),
    ("Figure 3", GENERATED / "figure3/pre_post_summary.svg"),
    ("Figure 4", GENERATED / "energy/figure4_monthly_energy_six_panel.svg"),
    ("Figure 5", GENERATED / "payments/figure5_capex_and_payments.svg"),
]


def sources(include_drafts: bool) -> list[tuple[str, Path]]:
    selected: list[tuple[str, Path]] = []
    seen: set[str] = set()
    for title, path in MAIN_FIGURES:
        if not path.is_file():
            raise FileNotFoundError(f"Required figure is missing: {path}")
        selected.append((title, path))
        seen.add(sha256(path.read_bytes()).hexdigest())
    if not include_drafts:
        return selected
    for path in sorted(GENERATED.rglob("*.svg")):
        digest = sha256(path.read_bytes()).hexdigest()
        if digest in seen:
            continue
        seen.add(digest)
        label = path.stem.replace("_", " ").capitalize()
        selected.append((label, path))
    return selected


def soffice_binary() -> str | None:
    override = os.environ.get("SOFFICE_BIN")
    if override:
        return override
    found = shutil.which("soffice")
    if found:
        return found
    bundled = Path(sys.executable).parents[2] / "bin" / "override" / "soffice"
    return str(bundled) if bundled.is_file() else None


def convert_svg(svg: Path, pdf: Path, profile: Path) -> None:
    """Preserve SVG text and shapes in PDF using available vector tooling."""
    office = soffice_binary()
    if office:
        command = [office, f"-env:UserInstallation={profile.as_uri()}", "--headless",
                   "--convert-to", "pdf", "--outdir", str(pdf.parent), str(svg)]
        env = os.environ.copy()
        env["XDG_CACHE_HOME"] = str(profile.parent / "font-cache")
        subprocess.run(command, check=True, capture_output=True, text=True,
                       timeout=180, env=env)
    else:
        try:
            from svglib.svglib import svg2rlg
            from reportlab.graphics import renderPDF
        except ImportError as exc:
            raise RuntimeError("Install LibreOffice or the publication extra: pip install -e '.[publication]'") from exc
        drawing = svg2rlg(str(svg))
        if drawing is None:
            raise ValueError(f"Could not parse {svg}")
        renderPDF.drawToFile(drawing, str(pdf))
    if not pdf.is_file():
        raise RuntimeError(f"SVG conversion did not create {pdf}")
    result = PdfReader(pdf)
    if len(result.pages) != 1 or not (result.pages[0].extract_text() or "").strip():
        raise RuntimeError(f"SVG conversion lost vector text: {svg}")


def assemble(figures: list[tuple[str, Path]], target: Path, width_inches: float) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    page_width = width_inches * 72
    artwork_width = page_width - 72  # 0.5-inch margins
    writer = PdfWriter()
    with tempfile.TemporaryDirectory(prefix="drc-figure-book-") as temp:
        scratch = Path(temp)
        pdf_dir = scratch / "pdf"
        pdf_dir.mkdir()
        profile = scratch / "libreoffice-profile"
        for index, (label, original) in enumerate(figures, 1):
            # Unique names avoid collisions between different generated folders.
            if original.suffix.lower() == ".pdf":
                artwork = PdfReader(original).pages[0]
            else:
                svg = scratch / f"figure_{index:02d}.svg"
                shutil.copyfile(original, svg)
                converted = pdf_dir / f"figure_{index:02d}.pdf"
                convert_svg(svg, converted, profile)
                artwork = PdfReader(converted).pages[0]
            source_width = float(artwork.mediabox.width)
            source_height = float(artwork.mediabox.height)
            scale = artwork_width / source_width
            artwork_height = source_height * scale
            page_height = artwork_height + 110
            buffer = BytesIO()
            plate = canvas.Canvas(buffer, pagesize=(page_width, page_height))
            plate.setFont("Helvetica-Bold", 24)
            plate.drawString(36, page_height - 44, label)
            plate.save()
            buffer.seek(0)
            page = PdfReader(buffer).pages[0]
            page.merge_transformed_page(
                artwork, Transformation().scale(scale).translate(36, 36), over=True
            )
            writer.add_page(page)
            writer.add_outline_item(f"{label}: {original.stem}", index - 1)
            print(f"{index:02d}. {label}: {original.relative_to(ROOT)}", flush=True)
    writer.add_metadata({"/Title": "North Kivu code-generated figures - large format"})
    with target.open("wb") as stream:
        writer.write(stream)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skip-analysis", action="store_true",
                        help="Package existing generated SVGs without rerunning the analysis.")
    parser.add_argument("--private-health", action="store_true",
                        help="Use local private DHIS2 inputs instead of the public panels.")
    parser.add_argument("--include-drafts", action="store_true",
                        help="Append additional generated analysis figures after Figures 1-5.")
    parser.add_argument("--width-inches", type=float, default=17.0,
                        help="PDF page width (default: 17 inches, 16-inch artwork width).")
    parser.add_argument("--output", type=Path, default=DEFAULT_PDF)
    args = parser.parse_args()
    if args.width_inches < 8:
        parser.error("--width-inches must be at least 8 for readable labels")
    if not args.skip_analysis:
        command = [sys.executable, str(ROOT / "scripts" / "run_all.py")]
        if not args.private_health:
            command.append("--from-public")
        subprocess.run(command, cwd=ROOT, check=True)
    subprocess.run([sys.executable, str(ROOT / "publication/figure1/build_figure1.py")],
                   cwd=ROOT, check=True)
    figures = sources(args.include_drafts)
    assemble(figures, args.output.resolve(), args.width_inches)
    print(f"Figure book: {args.output.resolve()} ({len(figures)} pages)")


if __name__ == "__main__":
    main()
