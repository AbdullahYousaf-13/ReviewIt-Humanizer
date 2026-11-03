"""Build the validation test set from test-images/own_test/{real,fake}.

Makes four versions of the same 100 images (50 real + 50 AI). Every version goes through the
SAME processing for real and AI, so file format and size cannot give the answer away:
  own_orig  the files exactly as downloaded (formats and sizes differ by source: second view)
  own_jpeg  RGB, re-saved as JPEG quality 85, no resize (MAIN RESULT: removes the PNG/WEBP clue)
  own_down  long side shrunk to 512 px, JPEG quality 90 (small thumbnails)
  own_shot  long side shrunk to 800 px, saved as PNG (like a screenshot of the image on screen)

Each folder gets a manifest.csv (file,label,model,subject,split) that score_smaug.py reads.
The split is fixed (seeded): tuning = 20 real + 20 AI, final = 30 real + 30 AI, balanced by
subject (real) and by subject and tool (AI). The decision threshold may only be tuned on the
tuning rows. The final rows are used once, to report the result.

Usage (from the repo root):
    .venv\\Scripts\\python.exe image-detection\\scripts\\build_testset.py
"""
import csv
import os
import random
import re

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.normpath(os.path.join(HERE, "..", "test-images"))
OWN = os.path.join(BASE, "own_test")
SUBJECTS = ["mountain", "coast", "forest", "street", "interior", "food", "flower", "animal", "monument", "vehicle"]
TOOLS = ["chatgpt", "gemini", "metaai", "leonardo", "recraft"]  # tool k made prompt variant k+1


def load_items():
    items = []
    rng = random.Random(2026)
    for s in SUBJECTS:  # real: 5 per subject -> 2 tuning, 3 final
        files = sorted(f for f in os.listdir(os.path.join(OWN, "real")) if f.startswith(s + "_"))
        assert len(files) == 5, (s, files)
        rng.shuffle(files)
        for i, f in enumerate(files):
            items.append({"src": f"real/{f}", "label": "real", "model": "openimages",
                          "subject": s, "split": "tuning" if i < 2 else "final"})
    for k, t in enumerate(TOOLS):  # AI: 10 per tool -> 4 tuning, 6 final; each subject tuned by 2 tools
        tuned = {SUBJECTS[(2 * k + j) % 10] for j in range(4)}
        for s in SUBJECTS:
            m = [f for f in os.listdir(os.path.join(OWN, "fake")) if re.match(rf"{t}__{s}-\d\.", f)]
            assert len(m) == 1, (t, s, m)
            items.append({"src": f"fake/{m[0]}", "label": "fake", "model": t,
                          "subject": s, "split": "tuning" if s in tuned else "final"})
    return items


def convert(im, cond):
    im = im.convert("RGB")
    if cond == "jpeg":
        return im, "jpg", {"quality": 85}
    long_side = {"down": 512, "shot": 800}[cond]
    w, h = im.size
    r = long_side / max(w, h)
    im = im.resize((round(w * r), round(h * r)), Image.LANCZOS)
    return (im, "jpg", {"quality": 90}) if cond == "down" else (im, "png", {})


def main():
    items = load_items()
    n = lambda lab, sp: sum(i["label"] == lab and i["split"] == sp for i in items)
    print(f"tuning: {n('real', 'tuning')} real + {n('fake', 'tuning')} AI; final: {n('real', 'final')} real + {n('fake', 'final')} AI")

    for cond in ["orig", "jpeg", "down", "shot"]:
        out = os.path.join(BASE, f"own_{cond}")
        rows = []
        for it in items:
            stem = os.path.splitext(os.path.basename(it["src"]))[0]
            if cond == "orig":
                rel = "../own_test/" + it["src"]
            else:
                im, ext, kw = convert(Image.open(os.path.join(OWN, it["src"])), cond)
                rel = f"{it['label']}/{stem}.{ext}"
                os.makedirs(os.path.join(out, it["label"]), exist_ok=True)
                im.save(os.path.join(out, rel), **kw)
            rows.append({"file": rel, "label": it["label"], "model": it["model"],
                         "subject": it["subject"], "split": it["split"]})
        os.makedirs(out, exist_ok=True)
        with open(os.path.join(out, "manifest.csv"), "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0]))
            w.writeheader()
            w.writerows(rows)
        print(f"{cond}: {len(rows)} images -> {out}")


if __name__ == "__main__":
    main()
