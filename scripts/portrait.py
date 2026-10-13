#!/usr/bin/env python3
"""Optional: turn a photo into a 1-bit dithered dot portrait (SVG).

Usage: python scripts/portrait.py photo.jpg [--size 300] [--out assets/portrait.svg]
Needs: pip install pillow
Then add to README.template.md:  <img src="assets/portrait.svg" width="300" />
"""
import argparse
from PIL import Image, ImageOps

ap = argparse.ArgumentParser()
ap.add_argument("photo")
ap.add_argument("--size", type=int, default=300, help="width in dots")
ap.add_argument("--out", default="assets/portrait.svg")
ap.add_argument("--color", default="#a78bfa")
a = ap.parse_args()

img = ImageOps.autocontrast(ImageOps.grayscale(Image.open(a.photo)))
h = int(img.height * a.size / img.width)
img = img.resize((a.size, h))
bw = img.convert("1")  # Floyd-Steinberg dithering by default

dots = []
for y in range(h):
    for x in range(a.size):
        if bw.getpixel((x, y)) == 0:  # dark pixel -> dot
            dots.append(f'<rect x="{x}" y="{y}" width="1" height="1"/>')

svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {a.size} {h}" width="{a.size}" height="{h}">'
       f'<rect width="100%" height="100%" fill="#0d1117"/><g fill="{a.color}">{"".join(dots)}</g></svg>')
open(a.out, "w").write(svg)
print(f"wrote {a.out} ({len(dots)} dots)")
