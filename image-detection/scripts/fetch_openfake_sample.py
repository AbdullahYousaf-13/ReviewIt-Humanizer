"""Download a small, labelled sample of the OpenFake test split for detector testing.

OpenFake (ComplexDataLab/OpenFake) is CC BY-NC 4.0: use it for testing only and never
commit the images (test-images/ is gitignored).

Each test parquet file is ~5 GB, so this reads only what it needs over HTTP:
  1. the small label/model columns of every row group in the chosen files;
  2. the image column of only the row groups that hold the picked rows.

Picking: real images at random; fake images round-robin over generators, so the
sample covers as many generators as possible instead of whatever happens to be first.

Usage (from the repo root):
    .venv\\Scripts\\python.exe image-detection\\scripts\\fetch_openfake_sample.py
    .venv\\Scripts\\python.exe image-detection\\scripts\\fetch_openfake_sample.py --split core --files 0,5 --n-real 50 --n-fake 50

Output: image-detection/test-images/openfake_<split>/{real,fake}/<row_id>.<ext>
        image-detection/test-images/openfake_<split>/manifest.csv
"""
import argparse
import csv
import io
import os
import random
from collections import defaultdict

import pyarrow.parquet as pq
from huggingface_hub import HfFileSystem
from PIL import Image

REPO = "datasets/ComplexDataLab/OpenFake"
NUM_FILES = {"core": 13, "reddit": 5}
META_COLS = ["label", "model", "type", "release_date", "row_id"]
HERE = os.path.dirname(os.path.abspath(__file__))
OUT_ROOT = os.path.normpath(os.path.join(HERE, "..", "test-images"))


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--split", default="core", choices=list(NUM_FILES))
    p.add_argument("--files", default="0", help="comma-separated test file indexes, e.g. 0,5,9")
    p.add_argument("--n-real", type=int, default=50)
    p.add_argument("--n-fake", type=int, default=50)
    p.add_argument("--seed", type=int, default=13)
    p.add_argument("--row-groups", type=int, default=4,
                   help="random row groups used per file (~100 MB each; rows are shuffled, "
                        "each group already holds 13-19 generators)")
    return p.parse_args()


def main():
    a = parse_args()
    rng = random.Random(a.seed)
    fs = HfFileSystem()
    n = NUM_FILES[a.split]
    paths = [f"{REPO}/{a.split}/test-{int(i):05d}-of-{n:05d}.parquet" for i in a.files.split(",")]

    # 1. metadata only: (file, row_group, row_in_group, meta)
    rows = []
    for path in paths:
        pf = pq.ParquetFile(fs.open(path))
        total = pf.metadata.num_row_groups
        rgs = sorted(rng.sample(range(total), min(a.row_groups, total)))
        for rg in rgs:
            t = pf.read_row_group(rg, columns=META_COLS).to_pylist()
            rows += [(path, rg, i, m) for i, m in enumerate(t)]
        print(f"read metadata: {path.split('/')[-1]} row groups {rgs} of {total}")
    real = [r for r in rows if r[3]["label"] == "real"]
    fake = [r for r in rows if r[3]["label"] == "fake"]
    by_model = defaultdict(list)
    for r in fake:
        by_model[r[3]["model"]].append(r)
    print(f"available: {len(real)} real, {len(fake)} fake from {len(by_model)} generators")

    # 2. pick
    picked = rng.sample(real, min(a.n_real, len(real)))
    pools = {m: rng.sample(v, len(v)) for m, v in by_model.items()}
    order = sorted(pools)
    fake_pick = []
    while len(fake_pick) < a.n_fake and any(pools.values()):
        for m in order:
            if pools[m] and len(fake_pick) < a.n_fake:
                fake_pick.append(pools[m].pop())
    picked += fake_pick

    # 3. images, one row group read per needed group
    out_dir = os.path.join(OUT_ROOT, f"openfake_{a.split}")
    need = defaultdict(list)
    for r in picked:
        need[(r[0], r[1])].append(r)
    manifest = []
    for (path, rg), items in sorted(need.items()):
        imgs = pq.ParquetFile(fs.open(path)).read_row_group(rg, columns=["image"]).column("image").to_pylist()
        for _, _, i, m in items:
            data = imgs[i]["bytes"]
            fmt = (Image.open(io.BytesIO(data)).format or "png").lower()
            ext = {"jpeg": "jpg"}.get(fmt, fmt)
            sub = os.path.join(out_dir, m["label"])
            os.makedirs(sub, exist_ok=True)
            fp = os.path.join(sub, f"{m['row_id']}.{ext}")
            with open(fp, "wb") as f:
                f.write(data)
            manifest.append({"file": os.path.relpath(fp, out_dir).replace("\\", "/"), **m})
        print(f"saved {len(items)} images from {path.split('/')[-1]} row group {rg}")

    with open(os.path.join(out_dir, "manifest.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["file"] + META_COLS)
        w.writeheader()
        w.writerows(manifest)
    n_gen = len({m["model"] for m in manifest if m["label"] == "fake"})
    print(f"done: {sum(m['label'] == 'real' for m in manifest)} real, "
          f"{sum(m['label'] == 'fake' for m in manifest)} fake ({n_gen} generators) -> {out_dir}")


if __name__ == "__main__":
    main()
