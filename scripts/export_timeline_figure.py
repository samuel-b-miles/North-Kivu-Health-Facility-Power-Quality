#!/usr/bin/env python3
"""Render the vector timeline figure to a true high-resolution PNG.

Run ``python scripts/run_timeline_figure.py`` first. Install the optional
``figures`` dependency group, then run this script. The SVG remains the
resolution-independent master.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import struct
import tempfile
import zlib

import cairosvg


ROOT = Path(__file__).resolve().parents[1]
SVG = ROOT / "outputs/generated/timeline/figure_implementation_monitoring_timeline.svg"
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def chunk(kind: bytes, data: bytes) -> bytes:
    return (struct.pack(">I", len(data)) + kind + data
            + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF))


def set_png_dpi(path: Path, dpi: int) -> None:
    """Write PNG pHYs metadata without decoding the large raster."""
    pixels_per_meter = round(dpi / 0.0254)
    phys = chunk(b"pHYs", struct.pack(">IIB", pixels_per_meter, pixels_per_meter, 1))
    with tempfile.NamedTemporaryFile(dir=path.parent, suffix=".png", delete=False) as tmp:
        temporary = Path(tmp.name)
        with path.open("rb") as src:
            if src.read(8) != PNG_SIGNATURE:
                raise ValueError(f"Not a PNG: {path}")
            tmp.write(PNG_SIGNATURE)
            inserted = False
            while True:
                size_bytes = src.read(4)
                if not size_bytes:
                    break
                size = struct.unpack(">I", size_bytes)[0]
                kind = src.read(4)
                data = src.read(size)
                crc = src.read(4)
                if kind == b"pHYs":
                    continue
                if kind == b"IDAT" and not inserted:
                    tmp.write(phys)
                    inserted = True
                tmp.write(size_bytes + kind + data + crc)
        if not inserted:
            raise ValueError(f"PNG has no IDAT chunk: {path}")
    temporary.chmod(path.stat().st_mode & 0o777)
    temporary.replace(path)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dpi", type=int, default=3600)
    parser.add_argument("--width-inches", type=float, default=7.5)
    args = parser.parse_args()
    if args.dpi <= 0 or args.width_inches <= 0:
        parser.error("dpi and width-inches must be positive")
    if not SVG.exists():
        parser.error(f"Run scripts/run_timeline_figure.py first: {SVG}")
    width_px = round(args.dpi * args.width_inches)
    output = SVG.with_name(f"{SVG.stem}_{args.dpi}dpi.png")
    cairosvg.svg2png(url=str(SVG), write_to=str(output), output_width=width_px)
    set_png_dpi(output, args.dpi)
    print(f"{output} ({width_px} pixels wide, {args.dpi} DPI)")


if __name__ == "__main__":
    main()
