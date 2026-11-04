"""Format check: save the 50 existing real photos as PNG (lossless) and WEBP (quality 90).

These are CONVERTED copies, not originals: each is a real JPEG re-saved in another format. They show whether a
real photo uploaded as PNG or WEBP is flagged more than the same photo as JPEG.

Writes test-images/own_formats/{png,webp}/<name>.<ext> and test-images/own_formats/manifest.csv
(file,label,model,subject,split). 'model' is converted_png or converted_webp.

Usage (from the repo root):
    .venv\\Scripts\\python.exe image-detection\\scripts\\build_format_check.py
"""
import csv
import os

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.normpath(os.path.join(HERE, "..", "test-images"))
SRC = os.path.join(BASE, "own_test", "real")
OUT = os.path.join(BASE, "own_formats")

rows = []
for name in sorted(os.listdir(SRC)):
    if not name.lower().endswith(".jpg"):
        continue
    stem, subject = os.path.splitext(name)[0], name.split("_")[0]
    im = Image.open(os.path.join(SRC, name)).convert("RGB")
    for fmt, ext, kw in [("png", "png", {}), ("webp", "webp", {"quality": 90})]:
        os.makedirs(os.path.join(OUT, fmt), exist_ok=True)
        im.save(os.path.join(OUT, fmt, f"{stem}.{ext}"), fmt.upper(), **kw)
        rows.append({"file": f"{fmt}/{stem}.{ext}", "label": "real", "model": f"converted_{fmt}", "subject": subject, "split": ""})
with open(os.path.join(OUT, "manifest.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0]))
    w.writeheader()
    w.writerows(rows)
print(f"{len(rows)} converted images -> {OUT} ({sum(r['model'] == 'converted_png' for r in rows)} PNG, {sum(r['model'] == 'converted_webp' for r in rows)} WEBP)")
