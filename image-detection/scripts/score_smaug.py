"""Score a labelled test set with abacusai/Smaug-AI-Image-Detector and report how well it did.

Reads test-images/<set>/manifest.csv (from fetch_openfake_sample.py), scores every image,
then prints and saves:
  - accuracy, AUC, AI images caught, real photos wrongly flagged (threshold 0.5 by default)
  - the same broken down by generator (fake) and by source (real)
  - CPU speed (model load time, seconds per image)

Usage (from the repo root):
    .venv\\Scripts\\python.exe image-detection\\scripts\\score_smaug.py
    .venv\\Scripts\\python.exe image-detection\\scripts\\score_smaug.py --set openfake_core --crops 1

Output: image-detection/results/smaug_<set>_crops<k>.csv (one row per image)
        image-detection/results/smaug_<set>_crops<k>_summary.txt
"""
import argparse
import csv
import os
import sys
import time
from collections import defaultdict

from huggingface_hub import snapshot_download
from sklearn.metrics import roc_auc_score

MODEL = "abacusai/Smaug-AI-Image-Detector"
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--set", default="openfake_core", help="folder under test-images/")
    p.add_argument("--crops", type=int, default=3, choices=[1, 3], help="3 = default/accurate, 1 = ~3x faster")
    p.add_argument("--threshold", type=float, default=0.5)
    p.add_argument("--batch-size", type=int, default=8)
    return p.parse_args()


def pct(a, b):
    return f"{100 * a / b:.1f}% ({a}/{b})" if b else "n/a"


def main():
    a = parse_args()
    set_dir = os.path.join(ROOT, "test-images", a.set)
    with open(os.path.join(set_dir, "manifest.csv"), encoding="utf-8") as f:
        items = list(csv.DictReader(f))

    t0 = time.perf_counter()
    path = snapshot_download(MODEL)
    sys.path.insert(0, path)
    from smaug_image_detect import SmaugImageDetect  # noqa: E402  (lives in the model repo)
    det = SmaugImageDetect.from_pretrained(path)
    load_s = time.perf_counter() - t0
    print(f"model loaded in {load_s:.1f}s on {det.st.device}")

    scores = []
    t1 = time.perf_counter()
    for i in range(0, len(items), a.batch_size):
        batch = items[i:i + a.batch_size]
        scores += det([os.path.join(set_dir, it["file"]) for it in batch], crops=a.crops, batch_size=a.batch_size)
        print(f"  scored {len(scores)}/{len(items)}", flush=True)
    per_img = (time.perf_counter() - t1) / len(items)

    y = [1 if it["label"] == "fake" else 0 for it in items]
    pred = [1 if s >= a.threshold else 0 for s in scores]
    n_fake, n_real = sum(y), len(y) - sum(y)
    caught = sum(p for p, t in zip(pred, y) if t == 1)
    flagged = sum(p for p, t in zip(pred, y) if t == 0)
    correct = sum(p == t for p, t in zip(pred, y))

    groups = defaultdict(lambda: [0, 0])  # name -> [correct, total]
    for it, p, t in zip(items, pred, y):
        key = ("AI   " if t else "REAL ") + it["model"]
        groups[key][0] += int(p == t)
        groups[key][1] += 1

    lines = [
        f"Smaug-AI-Image-Detector on test-images/{a.set} ({n_real} real, {n_fake} AI), crops={a.crops}, threshold={a.threshold}",
        f"Accuracy:                    {pct(correct, len(y))}",
        f"AUC:                         {roc_auc_score(y, scores):.4f}",
        f"AI images caught:            {pct(caught, n_fake)}",
        f"Real photos flagged as AI:   {pct(flagged, n_real)}",
        f"Speed (CPU):                 load {load_s:.1f}s, {per_img:.2f}s per image",
        "",
        "Correct by group (AI = generator, REAL = photo source):",
    ]
    lines += [f"  {k:<32} {pct(c, n)}" for k, (c, n) in sorted(groups.items())]
    report = "\n".join(lines)
    print("\n" + report)

    out = os.path.join(ROOT, "results")
    os.makedirs(out, exist_ok=True)
    stem = os.path.join(out, f"smaug_{a.set}_crops{a.crops}")
    with open(stem + ".csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["file", "label", "model", "subject", "split", "score", "predicted"])
        for it, s, p in zip(items, scores, pred):
            w.writerow([it["file"], it["label"], it["model"], it.get("subject", ""), it.get("split", ""),
                        f"{s:.4f}", "fake" if p else "real"])
    with open(stem + "_summary.txt", "w", encoding="utf-8") as f:
        f.write(report + "\n")
    print(f"\nsaved {stem}.csv and _summary.txt")


if __name__ == "__main__":
    main()
