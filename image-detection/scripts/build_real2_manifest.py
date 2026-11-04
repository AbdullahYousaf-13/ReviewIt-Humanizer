"""Write the manifest for the new real photos (test-images/own_test/real2) so the scoring scripts can read it.

Reads own_test/real2_sources.csv (from fetch_openimages_real.py) and writes test-images/own_real2/manifest.csv
with columns file,label,model,subject,split. The files are the original JPEGs, referenced in place.
The split is only a label here (seeded, stratified by subject: 25% cutoff part, 75% final part); the
analysis script re-splits ALL real photos (old and new) the same way.

Usage (from the repo root):
    .venv\\Scripts\\python.exe image-detection\\scripts\\build_real2_manifest.py
"""
import csv
import os
import random

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.normpath(os.path.join(HERE, "..", "test-images"))

rows = list(csv.DictReader(open(os.path.join(BASE, "own_test", "real2_sources.csv"), encoding="utf-8")))
rng = random.Random(2026)
by_subject = {}
for r in rows:
    by_subject.setdefault(r["subject"], []).append(r)
out = []
for s, items in sorted(by_subject.items()):
    rng.shuffle(items)
    cut = round(len(items) * 0.25)
    for i, r in enumerate(items):
        out.append({"file": "../own_test/" + r["file"], "label": "real", "model": "openimages2", "subject": s,
                    "split": "cutoff" if i < cut else "final"})
os.makedirs(os.path.join(BASE, "own_real2"), exist_ok=True)
with open(os.path.join(BASE, "own_real2", "manifest.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(out[0]))
    w.writeheader()
    w.writerows(out)
print(f"{len(out)} real photos -> own_real2/manifest.csv; per subject:", {s: len(v) for s, v in sorted(by_subject.items())})
