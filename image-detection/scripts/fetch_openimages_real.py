"""Pick 50 real photos (5 per subject) from Open Images for the image-detector test set.

Source: Hugging Face `vikhyatk/openimages-bbox` (test split). Open Images (V4, 2018) holds Flickr
photos, so every image predates 2020, i.e. predates photorealistic AI generators. The photos are
CC BY 2.0 on Flickr; use them for internal testing only and never commit them (test-images/ is
gitignored). Images are resized to at most 1024 px by the dataset authors.

The dataset has object labels but no scene labels, so subjects are assigned with CLIP zero-shot
(openai/clip-vit-base-patch32). Photos with people in them (Person/Man/Woman/Human face/...) are
skipped, and the original JPEG bytes are saved untouched.

Reads only a few ~30 MB row groups per shard over HTTP, never a whole 500 MB shard.

Usage (from the repo root):
    .venv\\Scripts\\python.exe image-detection\\scripts\\fetch_openimages_real.py
    .venv\\Scripts\\python.exe image-detection\\scripts\\fetch_openimages_real.py --per-subject 5 --seed 7

Output: image-detection/test-images/own_test/real/<subject>_<nn>.jpg
        image-detection/test-images/own_test/real_sources.csv
"""
import argparse
import csv
import io
import os
import random

import pyarrow.parquet as pq
import torch
from huggingface_hub import HfApi, HfFileSystem
from PIL import Image
from transformers import CLIPModel, CLIPProcessor

REPO = "vikhyatk/openimages-bbox"
CLIP = "openai/clip-vit-base-patch32"
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.normpath(os.path.join(HERE, "..", "test-images", "own_test"))

# subject -> CLIP prompt. Subjects must match the AI prompt list (docs/TEST_PROMPTS.md).
SUBJECTS = {
    "mountain": "a photo of mountains",
    "coast": "a photo of a beach or sea coast",
    "forest": "a photo of a forest with trees",
    "street": "a photo of a city street",
    "interior": "a photo of the inside of a room",
    "food": "a photo of food on a plate",
    "flower": "a photo of flowers",
    "animal": "a photo of an animal",
    "monument": "a photo of a historic building or monument",
    "vehicle": "a photo of a car, train or boat",
}
# classes that soak up photos that fit none of the subjects, so they are not forced into one
OTHER = ["a photo of a person", "a close-up photo of a small object", "a drawing or a diagram",
         "a photo of a sports event", "a photo of a night scene with lights", "a photo of a logo or text"]
PEOPLE = {"Person", "Man", "Woman", "Boy", "Girl", "Human face", "Human head", "Human body", "Child",
          "Human hair", "Human eye", "Human mouth", "Human nose", "Human hand", "Human arm", "Human leg",
          "Footwear", "Clothing", "Dress", "Suit", "Jeans", "Glasses", "Hat"}


def feats(out):
    """transformers 5 returns an output object from get_*_features; older versions a tensor."""
    x = out if isinstance(out, torch.Tensor) else out.pooler_output
    assert x.shape[-1] == 512, f"expected projected 512-d CLIP features, got {tuple(x.shape)}"
    return x / x.norm(dim=-1, keepdim=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--per-subject", type=int, default=5)
    ap.add_argument("--min-prob", type=float, default=0.6, help="CLIP confidence needed to assign a subject")
    ap.add_argument("--min-side", type=int, default=640, help="shorter image side in pixels")
    ap.add_argument("--max-groups", type=int, default=60, help="row groups to read at most")
    ap.add_argument("--seed", type=int, default=13)
    ap.add_argument("--out-name", default="real", help="folder under test-images/own_test/ for the photos")
    ap.add_argument("--sources-csv", default="real_sources.csv", help="record of where each photo came from")
    ap.add_argument("--exclude-csv", default="", help="a sources CSV whose photos must not be picked again")
    ap.add_argument("--prefix", default="", help="file name prefix, e.g. r2_")
    ap.add_argument("--pick", choices=["top", "random"], default="top",
                    help="top = photos CLIP finds most typical for the subject; random = random among those that qualify")
    ap.add_argument("--pool-factor", type=int, default=3, help="candidates to collect per subject = per-subject x this")
    a = ap.parse_args()
    rng = random.Random(a.seed)
    exclude = set()
    if a.exclude_csv:
        with open(os.path.join(OUT, a.exclude_csv), encoding="utf-8") as fh:
            exclude = {(r["shard"], int(r["row_group"]), int(r["row"])) for r in csv.DictReader(fh)}
        print(f"excluding {len(exclude)} photos already in {a.exclude_csv}")

    files = sorted(s.rfilename for s in HfApi().dataset_info(REPO).siblings
                   if s.rfilename.startswith("data/test-") and s.rfilename.endswith(".parquet"))
    fs = HfFileSystem()
    rng.shuffle(files)

    model = CLIPModel.from_pretrained(CLIP).eval()
    proc = CLIPProcessor.from_pretrained(CLIP)
    names = list(SUBJECTS) + ["other"] * len(OTHER)
    texts = list(SUBJECTS.values()) + OTHER
    with torch.no_grad():
        t = feats(model.get_text_features(**proc(text=texts, return_tensors="pt", padding=True)))

    pool = {s: [] for s in SUBJECTS}  # subject -> [(prob, bytes, meta)]
    seen, groups = 0, 0
    for path in files:
        if groups >= a.max_groups or all(len(v) >= a.per_subject * a.pool_factor for v in pool.values()):
            break
        pf = pq.ParquetFile(fs.open(f"datasets/{REPO}/{path}"))
        n_rg = pf.metadata.num_row_groups
        for rg in rng.sample(range(n_rg), min(2, n_rg)):
            groups += 1
            rows = pf.read_row_group(rg).to_pylist()
            imgs, keep = [], []
            for i, r in enumerate(rows):
                labels = {o["label"] for o in (r["objects"] or [])}
                if labels & PEOPLE:
                    continue
                im = Image.open(io.BytesIO(r["image"]["bytes"]))
                if im.format != "JPEG" or min(im.size) < a.min_side or max(im.size) / min(im.size) > 2.2:
                    continue
                imgs.append(im.convert("RGB"))
                keep.append((i, im.size, sorted(labels)))
            for b in range(0, len(imgs), 32):
                with torch.no_grad():
                    f = feats(model.get_image_features(**proc(images=imgs[b:b + 32], return_tensors="pt")))
                    p = (100 * f @ t.T).softmax(-1)
                for j in range(p.shape[0]):
                    sub_p = {s: 0.0 for s in SUBJECTS}
                    for k, nm in enumerate(names):
                        if nm in sub_p:
                            sub_p[nm] += p[j, k].item()
                    s, pr = max(sub_p.items(), key=lambda kv: kv[1])
                    if pr >= a.min_prob and (os.path.basename(path), rg, keep[b + j][0]) not in exclude:
                        i, size, labels = keep[b + j]
                        pool[s].append((pr, rows[i]["image"]["bytes"],
                                        {"shard": os.path.basename(path), "row_group": rg, "row": i,
                                         "size": f"{size[0]}x{size[1]}", "open_images_labels": ";".join(labels)}))
            seen += len(imgs)
            print(f"{os.path.basename(path)} rg{rg}: {seen} candidates, per subject: "
                  + " ".join(f"{s[:4]}={len(v)}" for s, v in pool.items()), flush=True)

    os.makedirs(os.path.join(OUT, a.out_name), exist_ok=True)
    manifest = []
    for s, items in pool.items():
        if len(items) < a.per_subject:
            print(f"WARNING: only {len(items)} confident photos for '{s}' (need {a.per_subject}); "
                  f"raise --max-groups or lower --min-prob")
        if a.pick == "random":
            chosen = rng.sample(items, min(a.per_subject, len(items)))
        else:
            chosen = sorted(items, key=lambda x: -x[0])[:a.per_subject]
        for n, (pr, data, meta) in enumerate(chosen, 1):
            name = f"{a.prefix}{s}_{n:02d}.jpg"
            with open(os.path.join(OUT, a.out_name, name), "wb") as fh:
                fh.write(data)
            manifest.append({"file": f"{a.out_name}/{name}", "subject": s, "clip_prob": f"{pr:.3f}", **meta})
    if manifest:
        with open(os.path.join(OUT, a.sources_csv), "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=list(manifest[0]))
            w.writeheader()
            w.writerows(manifest)
    print(f"done: {len(manifest)} real photos -> {OUT}")


if __name__ == "__main__":
    main()
