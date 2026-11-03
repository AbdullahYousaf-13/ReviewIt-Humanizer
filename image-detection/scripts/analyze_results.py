"""Report the validation result from results/smaug_own_<cond>_crops3.csv.

Rules that keep the result honest:
  - the decision threshold is chosen on the TUNING rows only (best balanced accuracy; ties go
    to the threshold closest to 0.5);
  - the numbers reported are for the FINAL rows (30 real + 30 AI), at that threshold, and also
    at the default 0.5;
  - every rate comes with a 95% Wilson interval, because 30 images per class is a small sample.

Usage (from the repo root):
    .venv\\Scripts\\python.exe image-detection\\scripts\\analyze_results.py
Output: printed, and saved to image-detection/results/smaug_own_report.txt
"""
import csv
import math
import os
from collections import defaultdict

from sklearn.metrics import roc_auc_score

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.normpath(os.path.join(HERE, "..", "results"))
CONDS = [("jpeg", "JPEG re-save q85 (MAIN)"), ("orig", "original files"),
         ("down", "shrunk to 512 px"), ("shot", "screenshot-style 800 px PNG")]


def wilson(k, n, z=1.96):
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0.0, c - h), min(1.0, c + h))


def rate(k, n):
    lo, hi = wilson(k, n)
    return f"{100 * k / n:5.1f}% ({k}/{n}, 95% range {100 * lo:.0f}-{100 * hi:.0f}%)" if n else "n/a"


def load(cond):
    with open(os.path.join(RES, f"smaug_own_{cond}_crops3.csv"), encoding="utf-8") as f:
        return [dict(r, score=float(r["score"])) for r in csv.DictReader(f)]


def counts(rows, thr):
    fake = [r for r in rows if r["label"] == "fake"]
    real = [r for r in rows if r["label"] == "real"]
    return (sum(r["score"] >= thr for r in fake), len(fake),
            sum(r["score"] >= thr for r in real), len(real))


def pick_threshold(tuning):
    best = None
    for thr in sorted({0.5} | {round(r["score"] + 1e-6, 6) for r in tuning} | {round(r["score"], 6) for r in tuning}):
        c, nf, fl, nr = counts(tuning, thr)
        bal = (c / nf + (nr - fl) / nr) / 2
        key = (bal, -abs(thr - 0.5))
        if best is None or key > best[0]:
            best = (key, thr)
    return best[1]


def main():
    out = []
    P = out.append
    P("Smaug-AI-Image-Detector, validation on our own test set (50 real Open Images + 50 AI from 5 free tools)")
    P("Final rows = 30 real + 30 AI. Threshold tuned on the 20 + 20 tuning rows only.\n")
    for cond, label in CONDS:
        path = os.path.join(RES, f"smaug_own_{cond}_crops3.csv")
        if not os.path.exists(path):
            P(f"[{cond}] not scored yet\n")
            continue
        rows = load(cond)
        tuning = [r for r in rows if r["split"] == "tuning"]
        final = [r for r in rows if r["split"] == "final"]
        thr = pick_threshold(tuning)
        y = [1 if r["label"] == "fake" else 0 for r in final]
        auc = roc_auc_score(y, [r["score"] for r in final])
        P(f"=== {label} ===")
        P(f"AUC (final): {auc:.3f}   tuned threshold: {thr:.3f}")
        for name, t in [("default 0.5", 0.5), (f"tuned {thr:.3f}", thr)]:
            c, nf, fl, nr = counts(final, t)
            P(f"  at {name:<12} AI caught {rate(c, nf)}")
            P(f"  {'':<15} real flagged {rate(fl, nr)}")
        c0, nf0, fl0, nr0 = counts(tuning, thr)
        P(f"  (tuning rows at tuned threshold: caught {c0}/{nf0}, real flagged {fl0}/{nr0})")
        by = defaultdict(lambda: [0, 0])
        for r in rows:  # per tool uses ALL 10 images per tool (descriptive only)
            if r["label"] == "fake":
                by[r["model"]][0] += r["score"] >= thr
                by[r["model"]][1] += 1
        P("  caught per tool (all 10 each, tuned threshold): " + ", ".join(f"{k} {v[0]}/{v[1]}" for k, v in sorted(by.items())))
        P("")
    text = "\n".join(out)
    print(text)
    with open(os.path.join(RES, "smaug_own_report.txt"), "w", encoding="utf-8") as f:
        f.write(text + "\n")


if __name__ == "__main__":
    main()
