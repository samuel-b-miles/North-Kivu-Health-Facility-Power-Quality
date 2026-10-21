#!/usr/bin/env python3
"""Typeset approved Table 1 and public-panel Table 2 as editable vector text.

Table 1's presentation source is publication/table1/source.json. It deliberately
has no caption, asterisk, or negotiated-fee footnote. Manuscript captions live
in the prose manuscript, outside this repository.
"""
from __future__ import annotations
import csv
import json
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph, Table, TableStyle

ROOT = Path(__file__).resolve().parents[1]
BODY = ParagraphStyle('body', fontName='Helvetica', fontSize=10, leading=14)
CENTER = ParagraphStyle('center', parent=BODY, alignment=TA_CENTER)
HEAD = ParagraphStyle('head', parent=CENTER, fontName='Helvetica-Bold', fontSize=9.5, leading=13)
NOTE = ParagraphStyle('note', parent=BODY, fontSize=9, leading=12)


def paragraph(value, style=BODY):
    if isinstance(value, list):
        value = '\n'.join(value)
    return Paragraph(escape(str(value)).replace('\n', '<br/>'), style)


def save_table(path, cells, widths, spans=(), note='', header_rows=1):
    path.parent.mkdir(parents=True, exist_ok=True)
    data = [[paragraph(value, HEAD if r < header_rows else (BODY if c == 1 else CENTER))
             for c, value in enumerate(row)] for r, row in enumerate(cells)]
    table = Table(data, colWidths=widths, repeatRows=header_rows)
    commands = [('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('TOPPADDING', (0, 0), (-1, -1), 12),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                ('LEFTPADDING', (0, 0), (-1, -1), 6),
                ('RIGHTPADDING', (0, 0), (-1, -1), 6),
                ('LINEABOVE', (0, 0), (-1, 0), 1.2, colors.black),
                ('LINEBELOW', (0, header_rows - 1), (-1, header_rows - 1), 1, colors.black),
                ('LINEBELOW', (0, -1), (-1, -1), 1.2, colors.black)]
    for row in range(header_rows, len(cells) - 1):
        commands.append(('LINEBELOW', (0, row), (-1, row), .35, colors.HexColor('#777777')))
    commands.extend(('SPAN', start, end) for start, end in spans)
    table.setStyle(TableStyle(commands))
    width, height = table.wrap(sum(widths), 1000)
    footnote = paragraph(note, NOTE) if note else None
    note_h = footnote.wrap(width, 1000)[1] if footnote else 0
    page_h = height + note_h + 60
    pdf = canvas.Canvas(str(path), pagesize=(width + 48, page_h), invariant=1)
    table.drawOn(pdf, 24, page_h - 24 - height)
    if footnote:
        footnote.drawOn(pdf, 24, 18)
    pdf.save()
    return path


def build_table1():
    source = json.loads((ROOT / 'publication/table1/source.json').read_text())
    columns = source['columns']
    cells = [[columns[0], columns[1], source['equipment_heading'], '', '', '', columns[6]],
             ['', '', *columns[2:6], ''], *source['rows']]
    spans = [((2, 0), (5, 0)), *(( (c, 0), (c, 1)) for c in (0, 1, 6))]
    return save_table(ROOT / 'publication/table1/table1.pdf', cells,
                      [48, 260, 85, 65, 70, 75, 117], spans,
                      source['definitions'], header_rows=2)


def build_table2():
    path = ROOT / 'outputs/generated/health/tables/table2_health_data_quality.csv'
    with path.open() as f:
        arms = {row['arm']: row for row in csv.DictReader(f)}
    metrics = [
        ('Facility-month reporting completeness (%)', 'facility_month_reporting_completeness_pct', 1),
        ('Ward-month reporting completeness (%)', 'ward_month_reporting_completeness_pct', 1),
        ('Facilities with uninterrupted monthly reporting', 'facilities_with_uninterrupted_reporting_n', None),
        ('Median longest continuous reporting streak (months)', 'median_longest_continuous_reporting_streak_months', 1),
        ('Facility-months with >0 reported deaths (%)', 'facility_months_with_deaths_pct', 1),
        ('Mean monthly admissions', 'mean_monthly_admissions', 1),
        ('Mean inpatient mortality rate (%)', 'mean_inpatient_mortality_rate_pct', 1)]
    cells = [['Monitoring metric', 'Treatment', 'Control']]
    for label, key, decimals in metrics:
        values = []
        for arm in ('treatment', 'control'):
            row = arms[arm]
            values.append(f"{int(float(row[key]))}/{int(float(row['facilities_total_n']))}" if decimals is None
                          else f'{float(row[key]):.{decimals}f}')
        cells.append([label, *values])
    return save_table(ROOT / 'publication/table2/table2.pdf', cells, [440, 140, 140])


if __name__ == '__main__':
    print(build_table1())
    print(build_table2())
