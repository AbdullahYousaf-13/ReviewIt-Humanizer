"""Format check result: are real photos flagged more when saved as PNG or WEBP than as the original JPEG?

Compares, photo by photo, the scores of the 50 real photos as original JPEG (results/*_own_orig*.csv) with their
PNG and WEBP copies (results/*_own_formats*.csv). The combined cutoffs come from analyze_combined.py
(results/combined_cutoffs.json); run that first.

Usage (from the repo root):
    .venv\\Scripts\\python.exe image-detection\\scripts\\analyze_formats.py
Output: printed, and saved to image-detection/results/format_check_report.txt
"""
import csv
import json
import os

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.normpath(os.path.join(HERE, "..", "results"))
EPS = 1e-6


def load(name):
    return {r["file"]: r for r in csv.DictReader(open(os.path.join(RES, name), encoding="utf-8"))}


def logit(x):
    x = min(max(float(x), EPS), 1 - EPS)
    return float(np.log(x / (1 - x)))


def main():
    S0, B0 = load("smaug_own_orig_crops3.csv"), load("bombek1_own_orig.csv")
    SF, BF = load("smaug_own_formats_crops3.csv"), load("bombek1_own_formats.csv")
    cut = json.load(open(os.path.join(RES, "combined_cutoffs.json")))
    t1, t10 = cut["cutoff_1pct"], cut["cutoff_10pct"]
    real = sorted(f for f in S0 if S0[f]["label"] == "real")
    out = [f"Format check: {len(real)} real photos, original JPEG vs the same photo saved as PNG and as WEBP (converted copies, not originals).",
           f"Combined cutoffs from the main test: 1% false-alarm cutoff {t1:.2f}, 10% cutoff {t10:.2f}.", "",
           f"{'format':6} | Smaug above 0.5 | Bombek1 above 0.5 | combined above 1% cutoff | combined above 10% cutoff | mean combined change vs JPEG | largest increase"]
    def comb(s, b): return (logit(s) + logit(b)) / 2
    base = {f: comb(S0[f]["score"], B0[f]["score"]) for f in real}
    rows = [("jpeg", {f: (float(S0[f]["score"]), float(B0[f]["score"])) for f in real})]
    for fmt in ["png", "webp"]:
        d = {}
        for f in real:
            key = f"{fmt}/{os.path.splitext(os.path.basename(f))[0]}.{fmt}"
            if key in SF and key in BF:
                d[f] = (float(SF[key]["score"]), float(BF[key]["score"]))
        rows.append((fmt, d))
    for fmt, d in rows:
        n = len(d)
        c = {f: comb(*v) for f, v in d.items()}
        delta = np.array([c[f] - base[f] for f in d]) if d else np.array([0.0])
        out.append(f"{fmt:6} | {sum(v[0] > .5 for v in d.values()):>3}/{n:<3} | {sum(v[1] > .5 for v in d.values()):>3}/{n:<3} | "
                   f"{sum(x > t1 for x in c.values()):>3}/{n:<3} | {sum(x > t10 for x in c.values()):>3}/{n:<3} | {delta.mean():+.2f} | {delta.max():+.2f}")
    out += ["", "Reading: if PNG and WEBP rows show more photos above the cutoffs than the JPEG row, real photos in those formats are flagged more.",
            "Limit: the copies are JPEGs re-saved as PNG or WEBP, not native PNG or WEBP photos."]
    text = "\n".join(out)
    print(text)
    open(os.path.join(RES, "format_check_report.txt"), "w", encoding="utf-8").write(text + "\n")


if __name__ == "__main__":
    main()
