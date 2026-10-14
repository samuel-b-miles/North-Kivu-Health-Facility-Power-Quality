#!/usr/bin/env python3
"""Rebuild manuscript Figure 1 from its three full-resolution source photos."""

from __future__ import annotations

from io import BytesIO
from pathlib import Path

from PIL import Image, ImageOps
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas


HERE = Path(__file__).resolve().parent
SOURCES = HERE / "sources"
OUTPUT = HERE / "figure1_full_frames.pdf"
PHOTOS = ("IMG_1769.JPG", "_MG_8649.JPG", "IMG_2207.jpg")


def build() -> Path:
    images = [ImageOps.exif_transpose(Image.open(SOURCES / name)).convert("RGB")
              for name in PHOTOS]
    width, margin, gap = 504, 5, 6
    image_height = (width - 2 * margin - 2 * gap) / sum(
        image.width / image.height for image in images
    )
    page_height = image_height + 23
    pdf = canvas.Canvas(str(OUTPUT), pagesize=(width, page_height), pageCompression=1)
    pdf.setTitle("Figure 1. Health facility electrification intervention components")
    x = margin
    for label, image in zip("abc", images):
        image_width = image_height * image.width / image.height
        pdf.setFont("Helvetica-Bold", 10)
        pdf.drawString(x, page_height - 12, label)
        buffer = BytesIO()
        image.save(buffer, format="JPEG", quality=95, subsampling=0, optimize=True)
        pdf.drawImage(ImageReader(buffer), x, margin,
                      width=image_width, height=image_height)
        x += image_width + gap
    pdf.save()
    return OUTPUT


if __name__ == "__main__":
    print(build())
