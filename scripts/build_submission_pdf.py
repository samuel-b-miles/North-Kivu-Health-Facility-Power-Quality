#!/usr/bin/env python3
"""Build the submission figures-and-tables PDF from reviewed assets.

No prose manuscript or journal captions are stored in this repository. This
build contains Figures 1-5 (Figure 3 on two pages) and Tables 1-2. Regenerating
scientific analyses is explicit and requires the existing restricted inputs.
"""
from __future__ import annotations
import argparse
from hashlib import sha256
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

import cairosvg
from pypdf import PdfReader
from PIL import Image, ImageOps

from build_figure_book import assemble
from build_submission_tables import build_table1, build_table2

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'outputs/generated/submission'


def run(script, *args):
    environment = os.environ.copy()
    environment["PYTHONPATH"] = str(ROOT / "src") + os.pathsep + environment.get("PYTHONPATH", "")
    subprocess.run([sys.executable, str(ROOT / script), *args], cwd=ROOT, env=environment, check=True)


def build(regenerate_analysis=False):
    OUT.mkdir(parents=True, exist_ok=True)
    if regenerate_analysis:
        run('scripts/run_all.py', '--from-public')
        for number, generated in [(4, 'energy/figure4_monthly_energy_six_panel.svg'),
                                   (5, 'payments/figure5_capex_and_payments.svg')]:
            shutil.copyfile(ROOT / 'outputs/generated' / generated,
                            ROOT / f'publication/figure{number}/figure{number}.svg')
    # Always rebuild presentation assets, even when reviewed analyses are reused.
    run('scripts/run_timeline_figure.py')
    run('scripts/export_timeline_figure.py', '--dpi', '600', '--width-inches', '7.5')
    timeline = ROOT / 'outputs/generated/timeline/figure_implementation_monitoring_timeline'
    figure2 = ROOT / 'publication/figure2/figure2'
    shutil.copyfile(str(timeline) + '.svg', str(figure2) + '.svg')
    shutil.copyfile(str(timeline) + '_600dpi.png', str(figure2) + '.png')
    cairosvg.svg2pdf(url=str(figure2) + '.svg', write_to=str(figure2) + '.pdf')
    # Keep the optional anchored-image replacement current as well.
    manuscript_image = ROOT / "publication/figure2/figure2_manuscript.png"
    with Image.open(manuscript_image) as old:
        manuscript_size = old.size
    with Image.open(str(figure2) + ".png") as current:
        fitted = ImageOps.contain(current.convert("RGB"), manuscript_size, Image.Resampling.LANCZOS)
    padded = Image.new("RGB", manuscript_size, "white")
    padded.paste(fitted, ((padded.width - fitted.width) // 2, (padded.height - fitted.height) // 2))
    padded.save(manuscript_image, dpi=(600, 600))
    # The compilation uses the unpadded vector PDF.
    run('scripts/run_health.py', '--from-public')
    table1, table2 = build_table1(), build_table2()
    sources = [
        ('Figure 1', ROOT / 'publication/figure1/figure1_full_frames.pdf'),
        ('Figure 2', Path(str(figure2) + '.pdf')),
        ('Figure 3', ROOT / 'publication/figure3/figure3_timeseries.svg'),
        ('Figure 3', ROOT / 'publication/figure3/figure3_summary.svg'),
        ('Figure 4', ROOT / 'publication/figure4/figure4.svg'),
        ('Figure 5', ROOT / 'publication/figure5/figure5.svg'),
        ('Table 1', table1), ('Table 2', table2)]
    converted = []
    manifest = []
    for index, (label, source) in enumerate(sources):
        artifact = source
        if source.suffix == '.svg':
            artifact = OUT / f'plate_{index + 1}.pdf'
            cairosvg.svg2pdf(url=str(source), write_to=str(artifact))
        converted.append((label, artifact))
        manifest.append({'label': label, 'source': str(source.relative_to(ROOT)),
                         'sha256': sha256(source.read_bytes()).hexdigest()})
    output = OUT / 'submission_figures_and_tables.pdf'
    assemble(converted, output, width_inches=11)
    reader = PdfReader(output)
    assert len(reader.pages) == 8
    table_text = reader.pages[6].extract_text()
    assert 'CSR3*' not in table_text and 'negotiated' not in table_text.lower()
    assert 'HGR=' in table_text and 'ICU=' in table_text
    assert 'Biomedical equipment (n=6)' in reader.pages[1].extract_text()
    assert 'Implementation, monitoring, and analytical windows' not in reader.pages[1].extract_text()
    (OUT / 'build_manifest.json').write_text(json.dumps({
        'scope': 'Figures 1-5 and Tables 1-2; no prose manuscript or captions',
        'sources': manifest}, indent=2) + '\n')
    print(output)
    return output


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--regenerate-analysis', action='store_true',
                        help='Rerun existing analyses with local restricted inputs before rebuilding reviewed Figures 4-5.')
    build(parser.parse_args().regenerate_analysis)
