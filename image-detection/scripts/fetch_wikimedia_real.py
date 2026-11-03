"""Download real photos from Wikimedia Commons for the image-detector test set.

A photo only counts as "certainly real" if it was uploaded BEFORE 2020 (before photorealistic
text-to-image generators existed) and has an open licence. This script keeps, per subject,
the first N search hits that pass all of these checks:
  - uploaded before 2020-01-01 (upload timestamp, the strong guarantee)
  - JPEG, original file 1000 px+ on the short side, under 12 MB
  - licence is Creative Commons or public domain
Originals are downloaded (not Commons' resized thumbnails) so the detector sees untouched pixels.

Usage (from the repo root):
    .venv\\Scripts\\python.exe image-detection\\scripts\\fetch_wikimedia_real.py
    .venv\\Scripts\\python.exe image-detection\\scripts\\fetch_wikimedia_real.py --per-subject 5

Output: image-detection/test-images/own_test/real/<subject>_<nn>.jpg
        image-detection/test-images/own_test/real_sources.csv  (title, author, licence, URL, dates)
"""
import argparse
import csv
import html
import os
import re
import sys
import time

import requests

# Needs commons.wikimedia.org to resolve (it did not on the author's network on 2026-11-03:
# fix DNS first, e.g. 8.8.8.8). The mobile hostname and api.wikimedia.org were tried and do not
# work: the first redirects here, the second only exposes the last-edit date, not the upload date.
API = "https://commons.wikimedia.org/w/api.php"
UA = {"User-Agent": "ReviewIt-image-detector-test/0.1 (research; contact: waleedyousaf07@gmail.com)"}
CUTOFF = "2020-01-01T00:00:00Z"
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.normpath(os.path.join(HERE, "..", "test-images", "own_test"))

# subject -> search terms. Subjects must match the AI prompt list (docs/TEST_PLAN.md).
SUBJECTS = {
    "mountain": "mountain landscape",
    "coast": "beach coast sea",
    "forest": "forest trees path",
    "street": "city street buildings",
    "interior": "room interior",
    "food": "food dish meal",
    "flower": "flower garden",
    "animal": "bird animal wildlife",
    "monument": "historic building monument",
    "vehicle": "car vehicle train",
}


def clean(s):
    return html.unescape(re.sub(r"<[^>]+>", "", s or "")).strip()


def search(term, limit=60):
    params = {
        "action": "query", "format": "json", "generator": "search", "gsrnamespace": 6,
        "gsrsearch": f'incategory:"Quality images" filetype:bitmap {term}', "gsrlimit": limit,
        "prop": "imageinfo", "iiprop": "url|size|mime|timestamp|extmetadata",
    }
    r = requests.get(API, params=params, headers=UA, timeout=60)
    r.raise_for_status()
    pages = r.json().get("query", {}).get("pages", {})
    return sorted(pages.values(), key=lambda p: p.get("index", 0))


def ok(page):
    ii = (page.get("imageinfo") or [{}])[0]
    meta = ii.get("extmetadata", {})
    lic = clean(meta.get("LicenseShortName", {}).get("value", ""))
    if ii.get("mime") != "image/jpeg" or ii.get("timestamp", "9") >= CUTOFF:
        return None
    if min(ii.get("width", 0), ii.get("height", 0)) < 1000 or ii.get("size", 0) > 12_000_000:
        return None
    if not (lic.startswith("CC") or lic.lower().startswith("public domain") or lic.upper() == "PD"):
        return None
    desc = clean(meta.get("ImageDescription", {}).get("value", "")).lower()
    if any(w in desc for w in ("ai-generated", "ai generated", "midjourney", "stable diffusion", "dall-e")):
        return None
    return ii, meta, lic


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--per-subject", type=int, default=5)
    a = ap.parse_args()
    os.makedirs(os.path.join(OUT, "real"), exist_ok=True)
    rows, seen = [], set()
    for subject, term in SUBJECTS.items():
        got = 0
        for page in search(term):
            if got >= a.per_subject:
                break
            title = page["title"]
            res = ok(page)
            if not res or title in seen:
                continue
            ii, meta, lic = res
            name = f"{subject}_{got + 1:02d}.jpg"
            fp = os.path.join(OUT, "real", name)
            if not os.path.exists(fp):
                img = requests.get(ii["url"], headers=UA, timeout=120)
                img.raise_for_status()
                with open(fp, "wb") as f:
                    f.write(img.content)
                time.sleep(1)  # be polite to Commons
            seen.add(title)
            got += 1
            rows.append({
                "file": f"real/{name}", "subject": subject, "title": title,
                "author": clean(meta.get("Artist", {}).get("value", "")),
                "licence": lic, "uploaded": ii["timestamp"],
                "taken": clean(meta.get("DateTimeOriginal", {}).get("value", "")),
                "size": f"{ii['width']}x{ii['height']}", "url": ii["descriptionurl"],
            })
            print(f"{name}: {title} [{lic}, uploaded {ii['timestamp'][:10]}]")
        if got < a.per_subject:
            print(f"WARNING: only {got}/{a.per_subject} for '{subject}'", file=sys.stderr)
    with open(os.path.join(OUT, "real_sources.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print(f"done: {len(rows)} real photos -> {OUT}")


if __name__ == "__main__":
    main()
