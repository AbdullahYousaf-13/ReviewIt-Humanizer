"""Choose the band limits for the combined detector: repeat the cutoff procedure on 500 random splits.

Combined score = average of Smaug and Bombek1 log-odds, original files (results/*_own_orig*.csv and *_own_real2*.csv).
Each round: the real photos are split at random (25% cutoff part, 75% final part, stratified by subject) and the
50 AI images are resampled with replacement. For an accuse limit A and a clear limit C the cutoffs come from the
cutoff part only (the score that only A, respectively C, of the real photos exceed). Photos above the accuse cutoff
are "likely AI", above the clear cutoff "unclear", the rest "likely real". Reports mean and 5th to 95th percentile.

Also prints the default cutoffs for the chosen limits (accuse 2%, clear 5%) computed from ALL real photos.

Usage (from the repo root):
    .venv\\Scripts\\python.exe image-detection\\scripts\\analyze_layouts.py
Output: printed, and saved to image-detection/results/layouts_report.txt
"""
import csv
import os
import random

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.normpath(os.path.join(HERE, "..", "results"))
EPS = 1e-6
N_SPLITS = 500
LAYOUTS = [(0.01, 0.05), (0.01, 0.10), (0.02, 0.05), (0.02, 0.10), (0.05, 0.10), (0.05, 0.20)]
CHOSEN = (0.02, 0.05)


def load(name):
    return {r["file"]: r for r in csv.DictReader(open(os.path.join(RES, name), encoding="utf-8"))}


def logit(p):
    p = min(max(float(p), EPS), 1 - EPS)
    return float(np.log(p / (1 - p)))


def fmt(v):
    return f"{np.mean(v):5.1f}% ({np.percentile(v, 5):4.1f} to {np.percentile(v, 95):4.1f})"


def main():
    rows = []
    for sf, bf in [("smaug_own_orig_crops3.csv", "bombek1_own_orig.csv"), ("smaug_own_real2_crops3.csv", "bombek1_own_real2.csv")]:
        S, B = load(sf), load(bf)
        for f in S:
            if f in B:
                rows.append(dict(y=1 if S[f]["label"] == "fake" else 0, subject=S[f]["subject"], comb=(logit(S[f]["score"]) + logit(B[f]["score"])) / 2))
    ai = np.array([r["comb"] for r in rows if r["y"] == 1])
    real = [r for r in rows if r["y"] == 0]
    subs = sorted({r["subject"] for r in real})
    by = {s: [r["comb"] for r in real if r["subject"] == s] for s in subs}
    keys = ["acc", "clear", "ai_acc", "ai_unc", "ai_clear"]
    res = {l: {k: [] for k in keys} for l in LAYOUTS}
    for seed in range(N_SPLITS):
        rng = random.Random(seed)
        cut, fin = [], []
        for s in subs:
            g = by[s][:]
            rng.shuffle(g)
            k = round(len(g) * 0.25)
            cut += g[:k]
            fin += g[k:]
        cut, fin = np.array(cut), np.array(fin)
        aib = ai[np.random.default_rng(seed).integers(0, len(ai), len(ai))]
        for a, c in LAYOUTS:
            th, tl = np.quantile(cut, 1 - a, method="higher"), np.quantile(cut, 1 - c, method="higher")
            d = res[(a, c)]
            d["acc"].append((fin > th).mean() * 100)
            d["clear"].append((fin <= tl).mean() * 100)
            d["ai_acc"].append((aib > th).mean() * 100)
            d["ai_clear"].append((aib <= tl).mean() * 100)
            d["ai_unc"].append(((aib > tl) & (aib <= th)).mean() * 100)
    out = [f"{N_SPLITS} random splits of {len(real)} real photos (25% cutoff part, 75% final part); {len(ai)} AI images resampled each time.",
           "Combined score = average of Smaug and Bombek1 log-odds, original files. Mean (5th to 95th percentile).", "",
           f"{'accuse / clear limit':20} | real accused         | real cleared          | AI accused            | AI left unclear       | AI wrongly cleared"]
    for a, c in LAYOUTS:
        d = res[(a, c)]
        mark = "  <- chosen" if (a, c) == CHOSEN else ""
        out.append(f"{int(a * 100)}% / {int(c * 100)}%".ljust(20) + f" | {fmt(d['acc'])} | {fmt(d['clear'])} | {fmt(d['ai_acc'])} | {fmt(d['ai_unc'])} | {fmt(d['ai_clear'])}{mark}")
    allr = np.array([r["comb"] for r in real])
    hi, lo = float(np.quantile(allr, 1 - CHOSEN[0], method="higher")), float(np.quantile(allr, 1 - CHOSEN[1], method="higher"))
    out += ["", f"Default cutoffs from all {len(real)} real photos (accuse limit {int(CHOSEN[0] * 100)}%, clear limit {int(CHOSEN[1] * 100)}%): accuse {hi:.2f}, clear {lo:.2f}"]
    for name, arr in [(f"real photos ({len(real)})", allr), (f"AI images ({len(ai)})", ai)]:
        n_ai, n_unc = int((arr > hi).sum()), int(((arr > lo) & (arr <= hi)).sum())
        out.append(f"  {name:20} likely AI {n_ai:>3} | unclear {n_unc:>3} | likely real {len(arr) - n_ai - n_unc:>3}   (in-sample, optimistic)")
    text = "\n".join(out)
    print(text)
    open(os.path.join(RES, "layouts_report.txt"), "w", encoding="utf-8").write(text + "\n")


if __name__ == "__main__":
    main()
