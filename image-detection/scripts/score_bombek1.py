"""Score a labelled test set with Bombek1/ai-image-detector-siglip-dinov2 (MIT) on CPU.

An ensemble of SigLIP2-SO400M (Apache 2.0) and DINOv2-Large (Apache 2.0) with LoRA adapters and a
small classifier head, about 740M parameters. sigmoid(logit) = probability the image is AI.

We run the authors' own model.py (MIT; read in full before use, revision pinned below) with three
changes, none of which alter the maths:
  - the two backbones are built from their config only, with no pretrained download: the checkpoint
    holds the complete weights and overwrites them anyway (saves about 4.5 GB of downloads);
  - the checkpoint is loaded with weights_only=True and strict=True (their code uses
    weights_only=False, which can run code from a pickle);
  - an image-reading helper that does not need the network.

Usage (from the repo root):
    .venv\\Scripts\\python.exe image-detection\\scripts\\score_bombek1.py --selfcheck
    .venv\\Scripts\\python.exe image-detection\\scripts\\score_bombek1.py --set own_jpeg

--selfcheck scores 20 labelled images from the OpenFake test sample (the data this model was trained
on and reports 99% on): if the loader were wrong, accuracy there would be poor.

Output for --set: image-detection/results/bombek1_<set>.csv and bombek1_<set>_summary.txt
"""
import argparse
import csv
import importlib.util
import os
import time
from collections import defaultdict

import torch
from huggingface_hub import hf_hub_download
from PIL import Image
from sklearn.metrics import roc_auc_score

REPO = "Bombek1/ai-image-detector-siglip-dinov2"
REVISION = "6455cf791436ee914c9556ab71578cce9761fef7"
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))


def load_model():
    mpath = hf_hub_download(REPO, "model.py", revision=REVISION)
    spec = importlib.util.spec_from_file_location("bombek1_model", mpath)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # the authors' file, reviewed in full

    # weights_only=True stays on. The checkpoint also stores a recorded metric as a NumPy number, so
    # only NumPy's number-rebuilding helpers are allowed (data only, they cannot run other code).
    import numpy as np
    safe = [np._core.multiarray.scalar, np.dtype] + [getattr(np.dtypes, n) for n in dir(np.dtypes) if n.endswith("DType")]
    with torch.serialization.safe_globals(safe):
        # mmap=True: read the 2.1 GB file from disk on demand instead of holding it all in RAM
        ckpt = torch.load(hf_hub_download(REPO, "pytorch_model.pt", revision=REVISION),
                          map_location="cpu", weights_only=True, mmap=True)
    cfg = ckpt.get("config", {})
    print("checkpoint config:", {k: cfg[k] for k in list(cfg)[:8]})

    # backbones from config only: no pretrained download (the checkpoint overwrites them)
    from transformers import SiglipVisionConfig, SiglipVisionModel
    import timm

    orig_sig, orig_timm = SiglipVisionModel.from_pretrained, timm.create_model

    def sig_from_config(name, torch_dtype=None, **kw):
        return SiglipVisionModel(SiglipVisionConfig.from_pretrained(name))

    def timm_no_pretrained(name, **kw):
        kw["pretrained"] = False
        return orig_timm(name, **kw)

    SiglipVisionModel.from_pretrained = staticmethod(sig_from_config)
    mod.timm.create_model = timm_no_pretrained
    try:
        # Build the model on the "meta" device: shapes only, no memory. The checkpoint tensors (memory-
        # mapped, already in the right precision: SigLIP bf16, DINOv2 fp32) are then attached directly
        # with assign=True, so the laptop never holds a second copy of the weights in RAM.
        with torch.device("meta"):
            model = mod.create_model_with_lora(
                siglip_model_name=cfg.get("siglip_model", "google/siglip2-so400m-patch14-384"),
                dinov2_model_name=cfg.get("dinov2_model", "vit_large_patch14_dinov2.lvd142m"),
                image_size=cfg.get("image_size", 392),
                lora_rank=cfg.get("lora_rank", 32), lora_alpha=cfg.get("lora_alpha", 64),
                lora_dropout=cfg.get("lora_dropout", 0.1))
    finally:
        SiglipVisionModel.from_pretrained = orig_sig
        mod.timm.create_model = orig_timm
    # The checkpoint was saved with an older transformers, which keeps SigLIP's weights under a
    # "vision_model." wrapper; transformers 5.x flattens it. Only that prefix is renamed (the tensors
    # are the same objects, nothing is copied); strict=True still fails on any other difference.
    old, new = "siglip.base_model.model.vision_model.", "siglip.base_model.model."
    state = {(new + k[len(old):] if k.startswith(old) else k): v for k, v in ckpt["model_state_dict"].items()}
    model.load_state_dict(state, strict=True, assign=True)  # any mismatch must fail loudly
    # buffers that are not in the checkpoint (SigLIP's position_ids is just 0..N-1) still sit on meta
    for mname, m in model.named_modules():
        for bname, buf in list(m._buffers.items()):
            if buf is not None and buf.is_meta:
                if bname != "position_ids":
                    raise RuntimeError(f"unexpected buffer left on meta: {mname}.{bname}")
                m._buffers[bname] = torch.arange(buf.shape[-1]).expand(*buf.shape).contiguous()
    left = [n for n, p in model.named_parameters() if p.is_meta]
    if left:
        raise RuntimeError(f"parameters left on meta: {left[:3]}")
    model.eval()

    from transformers import AutoProcessor
    proc = AutoProcessor.from_pretrained(cfg.get("siglip_model", "google/siglip2-so400m-patch14-384"))
    tf = mod.create_transforms(cfg.get("image_size", 392))
    return model, proc, tf


@torch.no_grad()
def score(bundle, paths, batch_size=4):
    model, proc, tf = bundle
    out = []
    for i in range(0, len(paths), batch_size):
        ims = [Image.open(p).convert("RGB") for p in paths[i:i + batch_size]]
        sig = proc(images=ims, return_tensors="pt")["pixel_values"]
        din = torch.stack([tf(im) for im in ims])
        logits, _, _ = model(sig, din)
        out += torch.sigmoid(logits).reshape(-1).tolist()
        print(f"  scored {len(out)}/{len(paths)}", flush=True)
    return out


def pct(a, b):
    return f"{100 * a / b:.1f}% ({a}/{b})" if b else "n/a"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--set", default="own_jpeg")
    ap.add_argument("--threshold", type=float, default=0.5)
    ap.add_argument("--batch-size", type=int, default=4)
    ap.add_argument("--selfcheck", action="store_true")
    a = ap.parse_args()

    t0 = time.perf_counter()
    bundle = load_model()
    load_s = time.perf_counter() - t0
    print(f"model loaded in {load_s:.1f}s, {sum(p.numel() for p in bundle[0].parameters()) / 1e6:.0f}M parameters")

    set_name = "openfake_core" if a.selfcheck else a.set
    set_dir = os.path.join(ROOT, "test-images", set_name)
    with open(os.path.join(set_dir, "manifest.csv"), encoding="utf-8") as f:
        items = list(csv.DictReader(f))
    if a.selfcheck:  # 10 real + 10 AI, spread over the file
        real = [i for i in items if i["label"] == "real"][::5][:10]
        fake = [i for i in items if i["label"] == "fake"][::5][:10]
        items = real + fake

    t1 = time.perf_counter()
    scores = score(bundle, [os.path.join(set_dir, it["file"]) for it in items], a.batch_size)
    per_img = (time.perf_counter() - t1) / len(items)

    y = [1 if it["label"] == "fake" else 0 for it in items]
    pred = [1 if s >= a.threshold else 0 for s in scores]
    n_fake, n_real = sum(y), len(y) - sum(y)
    caught = sum(p for p, t in zip(pred, y) if t == 1)
    flagged = sum(p for p, t in zip(pred, y) if t == 0)
    correct = sum(p == t for p, t in zip(pred, y))
    if a.selfcheck:
        print(f"\nSELF-CHECK on OpenFake sample: {correct}/{len(y)} correct, AI caught {caught}/{n_fake}, "
              f"real flagged {flagged}/{n_real}, AUC {roc_auc_score(y, scores):.3f}, {per_img:.1f}s per image")
        print("-> loader looks RIGHT" if correct >= 18 else "-> loader looks WRONG, do not trust results")
        return

    groups = defaultdict(lambda: [0, 0])
    for it, p, t in zip(items, pred, y):
        g = groups[("AI   " if t else "REAL ") + it["model"]]
        g[0] += int(p == t)
        g[1] += 1
    lines = [
        f"Bombek1 SigLIP2+DINOv2 on test-images/{a.set} ({n_real} real, {n_fake} AI), threshold={a.threshold}",
        f"Accuracy:                    {pct(correct, len(y))}",
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
    stem = os.path.join(out, f"bombek1_{a.set}")
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
