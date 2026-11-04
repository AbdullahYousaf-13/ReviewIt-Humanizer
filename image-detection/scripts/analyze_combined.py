"""Combined detector on ORIGINAL files: average of Smaug and Bombek1 log-odds, cutoff set from real photos only.

Data: 50 AI images + 50 real photos scored on the original files (results/*_own_orig*.csv) plus the new real
photos (results/*_own_real2*.csv). The AI images are NEVER used to choose a cutoff; they only measure the
catch rate. All real photos (old and new) are split, seeded and stratified by subject:
25% cutoff part (sets the cutoff), 75% final part (reports the false-alarm rate).

For each false-alarm limit L: cutoff = the score that only L of the cutoff-part real photos exceed.
Bands: likely AI = above the 1% cutoff; unclear = between the 10% and 1% cutoffs; likely real = below the 10% cutoff.

Usage (from the repo root):
    .venv\\Scripts\\python.exe image-detection\\scripts\\analyze_combined.py
Output: printed, and saved to image-detection/results/combined_originals_report.txt
"""
import csv
import math
import os
import random

import numpy as np
from sklearn.metrics import roc_auc_score

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.normpath(os.path.join(HERE, "..", "results"))
LIMITS = [0.005, 0.01, 0.02, 0.05]
EPS = 1e-6


def load(name):
    p = os.path.join(RES, name)
    return {r["file"]: r for r in csv.DictReader(open(p, encoding="utf-8"))} if os.path.exists(p) else {}


def logit(x):
    x = np.clip(np.asarray(x, dtype=float), EPS, 1 - EPS)
    return np.log(x / (1 - x))


def wilson(k, n, z=1.96):
    if n == 0:
        return "n/a"
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return f"{100 * max(0, c - h):.1f} to {100 * min(1, c + h):.1f}%"


def main():
    sets = [("smaug_own_orig_crops3.csv", "bombek1_own_orig.csv"), ("smaug_own_real2_crops3.csv", "bombek1_own_real2.csv")]
    rows = []
    for sf, bf in sets:
        S, B = load(sf), load(bf)
        for f in S:
            if f in B:
                rows.append(dict(file=f, y=1 if S[f]["label"] == "fake" else 0, tool=S[f]["model"], subject=S[f]["subject"],
                                 s=float(S[f]["score"]), b=float(B[f]["score"])))
    ai = [r for r in rows if r["y"] == 1]
    real = [r for r in rows if r["y"] == 0]
    # seeded split of ALL real photos, stratified by subject: 25% cutoff part, 75% final part
    rng = random.Random(2026)
    for sub in sorted({r["subject"] for r in real}):
        grp = [r for r in real if r["subject"] == sub]
        rng.shuffle(grp)
        for i, r in enumerate(grp):
            r["part"] = "cutoff" if i < round(len(grp) * 0.25) else "final"
    for r in rows:
        r["comb"] = float((logit(r["s"]) + logit(r["b"])) / 2)
        r["ls"], r["lb"] = float(logit(r["s"])), float(logit(r["b"]))
    cut = [r for r in real if r["part"] == "cutoff"]
    fin = [r for r in real if r["part"] == "final"]
    out = [f"Combined detector, original files. AI images {len(ai)}, real photos {len(real)} (cutoff part {len(cut)}, final part {len(fin)}).",
           "Score = average of Smaug and Bombek1 log-odds. Cutoff from the cutoff-part real photos only; AI images never used for the cutoff.", ""]
    scorers = [("Combined (average of log-odds)", "comb"), ("Smaug alone", "ls"), ("Bombek1 alone", "lb")]
    for name, key in scorers:
        auc = roc_auc_score([0] * len(fin) + [1] * len(ai), [r[key] for r in fin] + [r[key] for r in ai])
        out += [f"== {name}   (AUC final real vs all AI: {auc:.3f})",
                f"{'false-alarm limit':>18} | final real wrongly flagged | AI caught (of {len(ai)})"]
        cs = np.array([r[key] for r in cut])
        for L in LIMITS:
            t = np.quantile(cs, 1 - L, method="higher")
            fl = sum(r[key] > t for r in fin)
            ca = sum(r[key] > t for r in ai)
            out.append(f"{100 * L:>16.1f}% | {fl:>3}/{len(fin)} = {100 * fl / len(fin):4.1f}% (range {wilson(fl, len(fin))}) | {ca}/{len(ai)} = {100 * ca / len(ai):4.1f}% (range {wilson(ca, len(ai))})")
        out.append("")
    cs = np.array([r["comb"] for r in cut])
    t_hi, t_mid = np.quantile(cs, 0.99, method="higher"), np.quantile(cs, 0.90, method="higher")
    import json
    json.dump({"cutoff_1pct": float(t_hi), "cutoff_10pct": float(t_mid)}, open(os.path.join(RES, "combined_cutoffs.json"), "w"))
    band = lambda v: "likely AI" if v > t_hi else ("unclear" if v > t_mid else "likely real")
    out += [f"== Three bands (combined score): likely AI above {t_hi:.2f}; unclear {t_mid:.2f} to {t_hi:.2f}; likely real below {t_mid:.2f}",
            f"{'':14} | likely AI | unclear | likely real"]
    for nm, grp in [(f"real, final ({len(fin)})", fin), (f"AI ({len(ai)})", ai)]:
        c = {k: sum(band(r["comb"]) == k for r in grp) for k in ["likely AI", "unclear", "likely real"]}
        out.append(f"{nm:14} | {c['likely AI']:>9} | {c['unclear']:>7} | {c['likely real']:>11}")
    out += ["", f"== AI images caught per tool at the 1% limit (cutoff {t_hi:.2f})"]
    for tool in sorted({r["tool"] for r in ai}):
        g = [r for r in ai if r["tool"] == tool]
        out.append(f"{tool:10} {sum(r['comb'] > t_hi for r in g)}/{len(g)}")
    out += ["", "Limits: AI images are 50, so the catch rate has a range of about +-10 points; scores of the first 100 images are rounded to 4 decimals."]
    text = "\n".join(out)
    print(text)
    open(os.path.join(RES, "combined_originals_report.txt"), "w", encoding="utf-8").write(text + "\n")


if __name__ == "__main__":
    main()
