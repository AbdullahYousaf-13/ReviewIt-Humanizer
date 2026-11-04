"""Score a labelled test set with Community Forensics (OwensLab/commfor-model-384, MIT) on CPU.

A small ViT (vit_small_patch16_384, 21.8M parameters) with a 1-output head: sigmoid(output) is the
probability that the image is AI-generated. The loader is our own (no remote code is run): the
weights come from the model repo, the architecture from timm, and the preprocessing copies the
authors' test mode exactly: shorter side -> 440 px, centre crop 384, scale to 0-1, ImageNet
mean/std. Their code is MIT too (github.com/JeongsooP/Community-Forensics).

Usage (from the repo root):
    .venv\\Scripts\\python.exe image-detection\\scripts\\score_commfor.py --selfcheck
    .venv\\Scripts\\python.exe image-detection\\scripts\\score_commfor.py --set own_jpeg

--selfcheck scores the five DALL-E example images from the authors' notebook and compares them
with the numbers printed there (0.9988, 0.9878, 0.9569, 0.9516, 0.7860). Run it first.

Output for --set: image-detection/results/commfor_<set>.csv (one row per image)
                  image-detection/results/commfor_<set>_summary.txt
"""
import argparse
import csv
import os
import time
from collections import defaultdict

import timm
import torch
from huggingface_hub import hf_hub_download
from PIL import Image
from safetensors.torch import load_file
from sklearn.metrics import roc_auc_score
from torchvision import transforms

REPO = "OwensLab/commfor-model-384"
BASE = "vit_small_patch16_384.augreg_in21k_ft_in1k"  # architecture only; weights come from REPO
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))
NOTEBOOK = {"00000274": 0.9988, "00000420": 0.9878, "00000845": 0.9569, "00000916": 0.9516, "00000989": 0.7860}

TF = transforms.Compose([
    transforms.Resize(440),
    transforms.CenterCrop(384),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])


def load_model():
    m = timm.create_model(BASE, pretrained=False, num_classes=1)
    state = load_file(hf_hub_download(REPO, "model.safetensors"))
    state = {k[len("vit."):]: v for k, v in state.items()}
    m.load_state_dict(state, strict=True)  # strict: any mismatch must fail loudly
    return m.eval()


@torch.no_grad()
def score(model, paths, batch_size=16):
    out = []
    for i in range(0, len(paths), batch_size):
        x = torch.stack([TF(Image.open(p).convert("RGB")) for p in paths[i:i + batch_size]])
        out += torch.sigmoid(model(x)).squeeze(1).tolist()
        print(f"  scored {len(out)}/{len(paths)}", flush=True)
    return out


def pct(a, b):
    return f"{100 * a / b:.1f}% ({a}/{b})" if b else "n/a"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--set", default="own_jpeg")
    ap.add_argument("--threshold", type=float, default=0.5)
    ap.add_argument("--batch-size", type=int, default=16)
    ap.add_argument("--selfcheck", action="store_true")
    a = ap.parse_args()

    t0 = time.perf_counter()
    model = load_model()
    load_s = time.perf_counter() - t0
    print(f"model loaded in {load_s:.1f}s, {sum(p.numel() for p in model.parameters()) / 1e6:.1f}M parameters")

    if a.selfcheck:
        d = os.path.join(ROOT, "test-images", "commfor_examples")
        names = sorted(NOTEBOOK)
        got = score(model, [os.path.join(d, n + ".png") for n in names])
        print("\nimage      ours    authors' notebook (CUDA)")
        for n, g in zip(names, got):
            print(f"{n}  {g:.4f}  {NOTEBOOK[n]:.4f}")
        worst = max(abs(g - NOTEBOOK[n]) for n, g in zip(names, got))
        print(f"\nlargest difference: {worst:.4f}  ->  {'MATCHES' if worst < 0.02 else 'DOES NOT MATCH, do not trust results'}")
        return

    set_dir = os.path.join(ROOT, "test-images", a.set)
    with open(os.path.join(set_dir, "manifest.csv"), encoding="utf-8") as f:
        items = list(csv.DictReader(f))
    t1 = time.perf_counter()
    scores = score(model, [os.path.join(set_dir, it["file"]) for it in items], a.batch_size)
    per_img = (time.perf_counter() - t1) / len(items)

    y = [1 if it["label"] == "fake" else 0 for it in items]
    pred = [1 if s >= a.threshold else 0 for s in scores]
    n_fake, n_real = sum(y), len(y) - sum(y)
    caught = sum(p for p, t in zip(pred, y) if t == 1)
    flagged = sum(p for p, t in zip(pred, y) if t == 0)
    groups = defaultdict(lambda: [0, 0])
    for it, p, t in zip(items, pred, y):
        g = groups[("AI   " if t else "REAL ") + it["model"]]
        g[0] += int(p == t)
        g[1] += 1
    lines = [
        f"Community Forensics (commfor-model-384) on test-images/{a.set} ({n_real} real, {n_fake} AI), threshold={a.threshold}",
        f"Accuracy:                    {pct(sum(p == t for p, t in zip(pred, y)), len(y))}",
        f"AUC:                         {roc_auc_score(y, scores):.4f}",
        f"AI images caught:            {pct(caught, n_fake)}",
        f"Real photos flagged as AI:   {pct(flagged, n_real)}",
        f"Speed (CPU):                 load {load_s:.1f}s, {per_img:.2f}s per image",
        "",
        "Correct by group (AI = generator, REAL = photo source):",
    ] + [f"  {k:<32} {pct(c, n)}" for k, (c, n) in sorted(groups.items())]
    print("\n" + "\n".join(lines))

    out = os.path.join(ROOT, "results")
    os.makedirs(out, exist_ok=True)
    stem = os.path.join(out, f"commfor_{a.set}")
    with open(stem + ".csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["file", "label", "model", "subject", "split", "score", "predicted"])
        for it, s, p in zip(items, scores, pred):
            w.writerow([it["file"], it["label"], it["model"], it.get("subject", ""), it.get("split", ""),
                        f"{s:.4f}", "fake" if p else "real"])
    with open(stem + "_summary.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print(f"\nsaved {stem}.csv and _summary.txt")


if __name__ == "__main__":
    main()
