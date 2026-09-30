#!/usr/bin/env python3
"""Resize the original photos in ../images to web versions in public/images (max 1600px, ~200KB)."""
from pathlib import Path
from PIL import Image, ImageOps
SRC = Path(__file__).resolve().parents[2] / "images"
DST = Path(__file__).resolve().parents[1] / "public" / "images"
DST.mkdir(parents=True, exist_ok=True)
for f in sorted(SRC.glob("*.jpg")):
    im = ImageOps.exif_transpose(Image.open(f)).convert("RGB")
    im.thumbnail((1400, 1400))
    im.save(DST / f.name, "JPEG", quality=70, optimize=True, progressive=True)
    print(f.name, im.size, (DST / f.name).stat().st_size // 1024, "KB")
