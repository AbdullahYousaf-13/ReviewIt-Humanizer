"""
Local HF paraphrase-model test harness (separate from the LLM/Groq pipeline).

Tests sentence-level paraphrase models that run locally — no API, no rate limits.
Measures: speed (sentences/sec), and fact/citation preservation, and prints
side-by-side output so you can paste results into ZeroGPT / Copyleaks / GPTZero.

Usage:
    python test_local_models.py                      # run on built-in sample sentences
    python test_local_models.py sentences.txt        # one sentence per line
    python test_local_models.py --model humarin/chatgpt_paraphraser_on_T5_base
    python test_local_models.py --variants 3          # show N paraphrase candidates

First run downloads the model (~1 GB for humarin T5-base) to the HF cache.
"""

import argparse
import re
import sys
import time

import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

# --- Built-in research-paper-style sentences (10-40 words, with numbers + citations) ---
SAMPLE_SENTENCES = [
    "The implementation of deep neural networks enables the automated classification of medical images with remarkable accuracy.",
    "Prior work demonstrated a 23.4% improvement in diagnostic precision when convolutional architectures were employed (Smith et al., 2020).",
    "Furthermore, the integration of these computational methodologies facilitates the identification of pathological anomalies that conventional procedures fail to detect.",
    "Our model achieved an F1 score of 0.91 on the test set, outperforming the baseline reported by Chen and Kumar (2019).",
    "It is noteworthy that the aforementioned advancements have the potential to substantially reduce the probability of human diagnostic error.",
]

# citation patterns: (Smith et al., 2020), (Chen and Kumar, 2019), [12], etc.
CITATION_RE = re.compile(r"\([A-Z][A-Za-z]+(?:\s+(?:et al\.|and|&)\s+[A-Z][A-Za-z]+)?,?\s*\d{4}[a-z]?\)|\[\d+\]")
# numbers (ints, decimals, percentages)
NUMBER_RE = re.compile(r"\b\d+(?:\.\d+)?%?\b")


def paraphrase(text, model, tokenizer, device, num_return_sequences=1,
               num_beams=5, repetition_penalty=10.0,
               no_repeat_ngram_size=2, max_length=128, prefix=""):
    # Only T5-style models (humarin) need the "paraphrase: " prefix.
    input_ids = tokenizer(
        f"{prefix}{text}",
        return_tensors="pt",
        padding="longest",
        max_length=max_length,
        truncation=True,
    ).input_ids.to(device)

    # Plain beam search (transformers 5.x moved diverse/group beam search to a
    # remote-code repo). num_beams must be >= num_return_sequences.
    num_beams = max(num_beams, num_return_sequences)
    outputs = model.generate(
        input_ids,
        num_return_sequences=num_return_sequences,
        num_beams=num_beams,
        repetition_penalty=repetition_penalty,
        no_repeat_ngram_size=no_repeat_ngram_size,
        max_length=max_length,
    )
    return tokenizer.batch_decode(outputs, skip_special_tokens=True)


def check_preservation(original, rewritten):
    """Flag citations/numbers that were dropped or altered."""
    orig_cites = set(CITATION_RE.findall(original))
    new_cites = set(CITATION_RE.findall(rewritten))
    orig_nums = set(NUMBER_RE.findall(original))
    new_nums = set(NUMBER_RE.findall(rewritten))

    issues = []
    missing_cites = orig_cites - new_cites
    if missing_cites:
        issues.append(f"CITATION lost/changed: {sorted(missing_cites)}")
    missing_nums = orig_nums - new_nums
    if missing_nums:
        issues.append(f"NUMBER lost/changed: {sorted(missing_nums)}")
    return issues


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input", nargs="?", help="text file, one sentence per line")
    ap.add_argument("--model", default="humarin/chatgpt_paraphraser_on_T5_base")
    ap.add_argument("--variants", type=int, default=1, help="paraphrase candidates per sentence")
    args = ap.parse_args()

    if args.input:
        with open(args.input, "r", encoding="utf-8") as f:
            sentences = [ln.strip() for ln in f if ln.strip()]
    else:
        sentences = SAMPLE_SENTENCES

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Model : {args.model}")
    print(f"Device: {device}")
    print(f"Loading model (first run downloads weights)...\n")

    t0 = time.time()
    tokenizer = AutoTokenizer.from_pretrained(args.model)
    model = AutoModelForSeq2SeqLM.from_pretrained(args.model).to(device)
    model.eval()
    load_time = time.time() - t0
    n_params = sum(p.numel() for p in model.parameters())
    print(f"Loaded in {load_time:.1f}s | {n_params/1e6:.0f}M params")

    # T5-based models (humarin) require the "paraphrase: " task prefix; BART/PEGASUS do not.
    prefix = "paraphrase: " if "t5" in args.model.lower() else ""
    print(f"Prefix : {prefix!r}\n")

    # warm-up (first generate() call includes graph/compile overhead)
    with torch.no_grad():
        paraphrase(sentences[0], model, tokenizer, device, num_return_sequences=1, prefix=prefix)

    total_gen_time = 0.0
    out_lines = []
    any_issues = False

    for i, sent in enumerate(sentences, 1):
        with torch.no_grad():
            t = time.time()
            variants = paraphrase(sent, model, tokenizer, device,
                                  num_return_sequences=args.variants, prefix=prefix)
            dt = time.time() - t
        total_gen_time += dt

        print(f"[{i}/{len(sentences)}]  ({dt*1000:.0f} ms)")
        print(f"  ORIG: {sent}")
        for j, v in enumerate(variants, 1):
            tag = f"  OUT{j}:" if args.variants > 1 else "  OUT :"
            print(f"{tag} {v}")
            issues = check_preservation(sent, v)
            if issues:
                any_issues = True
                for issue in issues:
                    print(f"        !! {issue}")
        print()

        out_lines.append(variants[0])

    sps = len(sentences) / total_gen_time if total_gen_time else 0
    print("=" * 60)
    print(f"Sentences      : {len(sentences)}")
    print(f"Total gen time : {total_gen_time:.2f}s  (excludes load + warm-up)")
    print(f"Throughput     : {sps:.2f} sentences/sec  ({total_gen_time/len(sentences)*1000:.0f} ms/sentence)")
    print(f"Fact/cite flags: {'SOME ISSUES — see !! above' if any_issues else 'none detected'}")

    import os
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out_dir = os.path.join(root, "outputs")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "local_model_output.txt")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(out_lines))
    print(f"\nRewritten sentences saved to {out_path} (paste into detectors to test evasion)")


if __name__ == "__main__":
    main()
