#!/usr/bin/env python3
"""Render caption-free Table 1/2 PDFs to matching, print-ready PNGs."""
from __future__ import annotations
import argparse
from pathlib import Path
import pymupdf

ROOT=Path(__file__).resolve().parents[1]


def export_tables(width=4500,dpi=600):
    if width<=0 or dpi<=0:raise ValueError('width and dpi must be positive')
    outputs=[]
    for number in (1,2):
        source=ROOT/f'publication/table{number}/table{number}.pdf'
        target=source.with_suffix('.png')
        with pymupdf.open(source) as doc:
            if len(doc)!=1:raise ValueError(f'Expected one caption-free table page: {source}')
            page=doc[0];scale=width/page.rect.width
            pix=page.get_pixmap(matrix=pymupdf.Matrix(scale,scale),alpha=False)
            pix.set_dpi(dpi,dpi);pix.save(target)
            print(f'{target}: {pix.width} x {pix.height} pixels, {dpi} DPI')
        outputs.append(target)
    return outputs


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--width',type=int,default=4500)
    parser.add_argument('--dpi',type=int,default=600)
    args=parser.parse_args();export_tables(args.width,args.dpi)
