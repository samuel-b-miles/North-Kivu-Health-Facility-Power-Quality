#!/usr/bin/env python3
"""Render the publication timeline as a dependency-free SVG."""

from __future__ import annotations
from datetime import date
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs" / "generated" / "timeline"
OUT.mkdir(parents=True, exist_ok=True)

# Match the content bounds for a full-width manuscript figure: 90 px on each
# side of the widest element and a small margin above and below the artwork.
W, H = 1600, 1200
X0, X1 = 410, 1375
START, END = date(2022, 1, 1), date(2026, 6, 1)
# Publication/export palette. The earlier version read too pale after
# Google Slides/Docs import, so these colors are deliberately darker.
INK, MUTED, GRID = "#101820", "#3f4d56", "#c5cdd2"
BLUE, BLUE_LIGHT, CONTEXT = "#1f5f7a", "#b7d6e3", "#9a503f"
DOC_FILL, DOC_STROKE = "#d9dde0", "#5f6c73"
CONTEXT_FILL = "#ead3ca"


def x(day: date) -> float:
    return X0 + (day - START).days / (END - START).days * (X1 - X0)


def bar(parts, y, start, end, kind="data"):
    xs, xe = x(date.fromisoformat(start)), x(date.fromisoformat(end))
    if kind == "data":
        parts.append(f'<rect x="{xs:.1f}" y="{y-15}" width="{xe-xs:.1f}" height="30" rx="2" fill="{BLUE_LIGHT}" stroke="{BLUE}" stroke-width="2.1"/>')
    elif kind == "implementation":
        parts.append(f'<rect x="{xs:.1f}" y="{y-15}" width="{xe-xs:.1f}" height="30" rx="2" fill="{DOC_FILL}" stroke="{DOC_STROKE}" stroke-width="2.1"/>')
    else:
        parts.append(f'<rect x="{xs:.1f}" y="{y-15}" width="{xe-xs:.1f}" height="30" rx="2" fill="url(#hatch)" stroke="{CONTEXT}" stroke-width="2.1"/>')


def label(parts, y, text, n, span):
    bits = text.split("\n")
    for i, bit in enumerate(bits):
        yy = y - (len(bits)-1)*10 + i*20
        parts.append(f'<text x="375" y="{yy+5}" text-anchor="end" class="row">{escape(bit)}</text>')


parts = [f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<defs><style>
.title{{font:700 26px Arial,sans-serif;fill:{INK}}}.panel{{font:700 24px Arial,sans-serif;fill:{INK}}}
.row{{font:17px Arial,sans-serif;fill:{INK}}}.meta{{font:15px Arial,sans-serif;fill:{MUTED}}}
.axis{{font:14px Arial,sans-serif;fill:{MUTED}}}.note{{font:14px Arial,sans-serif;fill:{MUTED}}}
</style><pattern id="hatch" patternUnits="userSpaceOnUse" width="9" height="9" patternTransform="rotate(45)"><rect width="9" height="9" fill="{CONTEXT_FILL}"/><line x1="0" y1="0" x2="0" y2="9" stroke="{CONTEXT}" stroke-width="2.4" opacity=".9"/></pattern></defs>
<rect width="100%" height="100%" fill="white"/>
<text x="90" y="55" class="title">Implementation, monitoring, and analytical windows</text>
''']

# Shared timeline grid.
for panel_top, panel_bottom in [(120, 685), (785, 1085)]:
    for year in range(2022, 2027):
        for month in (1, 7):
            d = date(year, month, 1)
            if d > END: continue
            xx=x(d); parts.append(f'<line x1="{xx:.1f}" y1="{panel_top}" x2="{xx:.1f}" y2="{panel_bottom}" stroke="{GRID}" stroke-width="1"/>')
    intervention=x(date(2024,5,1)); parts.append(f'<line x1="{intervention:.1f}" y1="{panel_top}" x2="{intervention:.1f}" y2="{panel_bottom}" stroke="{INK}" stroke-width="1.7" stroke-dasharray="5,5" opacity=".9"/>')

parts += ['<text x="90" y="108" class="panel">A  Implementation and service delivery</text>']
rows_a = [
    (165,"Electricity supply baseline -\nlongitudinal (n=3)","n=3","≈29 mo","2022-01-01","2024-05-01","data"),
    (225,"Electricity supply baseline -\nshort (n=3)","n=3","25–28 d each","2024-01-01","2024-08-01","data"),
    (285,"Pre-installation surveys","n=15","7-mo window","2023-09-01","2024-04-30","implementation"),
    (345,"Intervention deployment","n=6","Apr–May 2024","2024-04-01","2024-06-01","implementation"),
    (405,"Biomedical equipment","n=6","≈1 mo","2024-05-15","2024-06-15","implementation"),
    (465,"Post-intervention telemetry","n=6","≤20 mo","2024-05-22","2026-01-12","data"),
    (525,"Facility payment model","n=6","Apr 2024–Apr 2026","2024-04-02","2026-04-06","data"),
    (585,"Conflict-related operational\ndisruption","n=2","≈3 mo","2025-01-01","2025-04-01","context"),
]
for y,t,n,s,a,b,k in rows_a:
    parts.append(f'<line x1="{X0}" y1="{y}" x2="{X1}" y2="{y}" stroke="#dfe5e8"/>'); label(parts,y,t,n,s); bar(parts,y,a,b,k)

parts += ['<line x1="90" y1="735" x2="1510" y2="735" stroke="#aeb8bd" stroke-width="1"/>',
          '<text x="90" y="775" class="panel">B  Measurement and analytical windows</text>']
rows_b = [
    (835,"DHIS2 health outcomes","n=12","36 monthly periods","2023-01-01","2026-01-01","data"),
    (895,"Energy demand telemetry\n(Prospect)","n=6","up to 20 mo","2024-05-22","2026-01-12","data"),
    (955,"Paired energy demand\nand supply telemetry\n(Prospect and GridWatch)","n=6","facility-specific","2024-05-22","2025-11-25","data"),
    (1015,"Payment and maintenance ledger","n=6","25 monthly periods","2024-04-02","2026-04-06","data"),
]
for y,t,n,s,a,b,k in rows_b:
    parts.append(f'<line x1="{X0}" y1="{y}" x2="{X1}" y2="{y}" stroke="#dfe5e8"/>'); label(parts,y,t,n,s); bar(parts,y,a,b,k)

# Axes and labels.
for axis_y in (650,1080):
    parts.append(f'<line x1="{X0}" y1="{axis_y}" x2="{X1}" y2="{axis_y}" stroke="{INK}" stroke-width="1"/>')
    for year in range(2022, 2027):
        for month,label_text in ((1,f'Jan {year}'),(7,f'Jul {year}')):
            d=date(year,month,1)
            if d>END: continue
            xx=x(d); parts.append(f'<line x1="{xx:.1f}" y1="{axis_y}" x2="{xx:.1f}" y2="{axis_y+7}" stroke="{INK}"/>')
            parts.append(f'<text x="{xx:.1f}" y="{axis_y+27}" text-anchor="end" transform="rotate(-35 {xx:.1f} {axis_y+27})" class="axis">{label_text}</text>')
parts.append(f'<text x="{x(date(2024,5,1))+8:.1f}" y="142" class="axis" font-weight="bold">Intervention period begins</text>')

# Legend.
parts += [f'<rect x="90" y="1150" width="28" height="16" fill="{BLUE_LIGHT}" stroke="{BLUE}"/><text x="128" y="1164" class="note">Time-series data</text>',
          f'<rect x="380" y="1150" width="28" height="16" fill="{DOC_FILL}" stroke="{DOC_STROKE}"/><text x="418" y="1164" class="note">Program documentation</text>',
          f'<rect x="790" y="1150" width="28" height="16" fill="url(#hatch)" stroke="{CONTEXT}"/><text x="828" y="1164" class="note">Contextual disruption</text>',
          '</svg>']

(OUT / 'figure_implementation_monitoring_timeline.svg').write_text('\n'.join(parts), encoding='utf-8')
print(OUT / 'figure_implementation_monitoring_timeline.svg')
