"""
Test harness: local Hugging Face paraphrase MODELS for sentence-level humanization.
Mirrors scripts/test_humanizer_api_llms.py, but uses offline seq2seq models instead of
prompted API LLMs. See docs/MODEL_RESEARCH.md.

Models (offline, no API; run on CPU):
  bart      eugenesiow/bart-paraphrase                 (BART-large, ~406M)
  pegasus   tuner007/pegasus_paraphrase                (PEGASUS, ~569M)
  humarin   humarin/chatgpt_paraphraser_on_T5_base     (T5-base, ~223M)

NOTE: these are NOT prompted — they are fixed paraphrasers. You feed a sentence, they return a
paraphrase; behaviour is baked in at training time (no A/B/C prompt variants).

What it does:
  - Runs a set of AI-flagged sentences (or your own, one per line) through the chosen model,
    one sentence at a time.
  - FIDELITY check: every number and in-text citation in the original must survive verbatim,
    and none may be added (same checker as the API harness).
  - Saves to data/<model>/output.txt: numbered INPUT/OUTPUT sections, with each sentence on its
    OWN LINE (not merged into a paragraph), so INPUT and OUTPUT lines line up 1:1.

It does NOT call any AI detector — paste the OUTPUT sentences into ZeroGPT/GPTZero/Copyleaks.

Usage:
    python scripts/test_humanizer_models.py                      # bart, built-in samples
    python scripts/test_humanizer_models.py pegasus              # pegasus, built-in samples
    python scripts/test_humanizer_models.py bart my_sents.txt    # one sentence per line
    python scripts/test_humanizer_models.py <any/hf-model-id> my_sents.txt

First run downloads the model weights to the Hugging Face cache.
"""

import os
import re
import sys
import time

import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

# --- Model registry ----------------------------------------------------------
MODELS = {
    "bart": "eugenesiow/bart-paraphrase",
    "pegasus": "tuner007/pegasus_paraphrase",
    "humarin": "humarin/chatgpt_paraphraser_on_T5_base",
}
DEFAULT_MODEL = "bart"

# --- Built-in test set (same as the API harness, for comparability) ----------
SAMPLE_SENTENCES = [
    "The implementation of deep neural networks demonstrated a classification accuracy of 94.3% on the held-out test set.",
    "Furthermore, the proposed methodology significantly outperformed baseline approaches (p < 0.001), as reported by Chen et al. (2021).",
    "It is noteworthy that the aforementioned intervention reduced patient mortality by approximately 27% over a 12-month period.",
    "The utilization of transfer learning facilitated a substantial reduction in training time, consistent with prior findings (Smith & Jones, 2019).",
    "These results suggest that the integration of multimodal data sources enhances predictive performance across heterogeneous populations.",
    "The experimental cohort comprised 1,482 participants recruited from three independent clinical sites between 2018 and 2020.",
    "Consequently, the model achieved an F1-score of 0.87, thereby exceeding the previous state-of-the-art benchmark [14].",
    "The observed correlation between the two variables was statistically significant (r = 0.62, p = 0.004).",
]

# --- Fidelity checking (identical to the API harness) ------------------------
NUM_RE = re.compile(r"\b\d[\d,]*\.?\d*%?\b")
CITE_RE = re.compile(
    r"\[\d+\]"
    r"|[A-Z][A-Za-z]+(?:\s+(?:et al\.?|&\s*[A-Z][A-Za-z]+|and\s+[A-Z][A-Za-z]+))?\s*\(\d{4}[a-z]?\)"
    r"|\([^()]*?\b\d{4}[a-z]?\b[^()]*?\)"
)


def _norm_numbers(text):
    t = text.lower().replace("percent", "%")
    t = re.sub(r"(\d)\s*%", r"\1%", t)
    t = re.sub(r"(?<=\d),(?=\d)", "", t)
    return t


def extract_facts(text):
    nums = set(NUM_RE.findall(_norm_numbers(text)))
    cites = set(c.strip() for c in CITE_RE.findall(text))
    return nums, cites


def fidelity_check(original, rewrite):
    """Return (ok, missing_nums, added_nums, missing_cites, added_cites)."""
    o_nums, o_cites = extract_facts(original)
    r_nums, r_cites = extract_facts(rewrite)
    missing_nums = sorted(o_nums - r_nums)
    added_nums = sorted(r_nums - o_nums)
    missing_cites = sorted(o_cites - r_cites)
    added_cites = sorted(r_cites - o_cites)
    ok = not (missing_nums or added_nums or missing_cites or added_cites)
    return ok, missing_nums, added_nums, missing_cites, added_cites


# --- Model inference ---------------------------------------------------------
def paraphrase(text, model, tokenizer, device, prefix="",
               num_beams=5, repetition_penalty=10.0,
               no_repeat_ngram_size=2, max_length=128):
    input_ids = tokenizer(
        f"{prefix}{text}", return_tensors="pt", padding="longest",
        max_length=max_length, truncation=True,
    ).input_ids.to(device)
    outputs = model.generate(
        input_ids, num_return_sequences=1, num_beams=num_beams,
        repetition_penalty=repetition_penalty,
        no_repeat_ngram_size=no_repeat_ngram_size, max_length=max_length,
    )
    return tokenizer.batch_decode(outputs, skip_special_tokens=True)[0].strip()


# --- CLI / main --------------------------------------------------------------
def parse_args():
    args = sys.argv[1:]
    model_key = None
    if args and (args[0] in MODELS or "/" in args[0]):   # alias or full HF id
        model_key = args.pop(0)
    elif args and not os.path.exists(args[0]):
        print(f"'{args[0]}' is not a known model or an existing file.\n"
              f"Models: {', '.join(MODELS)} (or a full HF model id)")
        sys.exit(1)
    model_key = model_key or DEFAULT_MODEL
    sentences_file = args[0] if args else None

    if model_key in MODELS:
        model_id, alias = MODELS[model_key], model_key
    else:                                                 # full HF id passed
        model_id, alias = model_key, model_key.split("/")[-1]
    return model_id, alias, sentences_file


def load_sentences(sentences_file):
    if sentences_file:
        with open(sentences_file, "r", encoding="utf-8") as f:
            lines = [ln.strip() for ln in f if ln.strip()]
        print(f"Loaded {len(lines)} sentences from {sentences_file}")
        return lines
    print(f"Using {len(SAMPLE_SENTENCES)} built-in sample sentences")
    return SAMPLE_SENTENCES


def next_section(path):
    if not os.path.exists(path):
        return 1
    with open(path, "r", encoding="utf-8") as f:
        nums = [int(m.group(1)) for m in re.finditer(r"(?m)^# (\d+)\s*$", f.read())]
    return (max(nums) + 1) if nums else 1


def main():
    model_id, alias, sentences_file = parse_args()
    sentences = load_sentences(sentences_file)

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Model: {model_id}  (alias: {alias}) | device: {device}")
    print("Loading model (first run downloads weights)...")
    t0 = time.time()
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_id).to(device)
    model.eval()
    n_params = sum(p.numel() for p in model.parameters())
    prefix = "paraphrase: " if "t5" in model_id.lower() else ""   # only T5 needs the prefix
    print(f"Loaded in {time.time() - t0:.1f}s | {n_params / 1e6:.0f}M params | prefix={prefix!r}\n")

    with torch.no_grad():   # warm-up (first generate includes graph overhead)
        paraphrase(sentences[0], model, tokenizer, device, prefix=prefix)

    outputs = []
    totals = {"n": 0, "fidelity_fail": 0, "gen_s": 0.0}

    for i, sent in enumerate(sentences, 1):
        with torch.no_grad():
            t = time.time()
            rewrite = paraphrase(sent, model, tokenizer, device, prefix=prefix)
            dt = time.time() - t
        ok, miss_n, add_n, miss_c, add_c = fidelity_check(sent, rewrite)
        totals["n"] += 1
        totals["gen_s"] += dt
        if not ok:
            totals["fidelity_fail"] += 1
        flag = "OK " if ok else "FACT-LOSS"
        print(f"[{i}/{len(sentences)}] [{flag}] {dt * 1000:.0f}ms")
        print(f"  ORIG: {sent}")
        print(f"  OUT : {rewrite}")
        if miss_n:
            print(f"        missing numbers: {miss_n}")
        if add_n:
            print(f"        ADDED numbers (hallucination?): {add_n}")
        if miss_c:
            print(f"        missing citations: {miss_c}")
        if add_c:
            print(f"        ADDED citations (fabricated reference!): {add_c}")
        outputs.append(rewrite)

    # --- Save: data/<model>/output.txt, numbered sections, one sentence per line ---
    model_dir = os.path.normpath(os.path.join(
        os.path.dirname(__file__), "..", "data", alias))
    os.makedirs(model_dir, exist_ok=True)
    path = os.path.join(model_dir, "output.txt")
    n = next_section(path)
    with open(path, "a", encoding="utf-8") as f:
        f.write(f"# {n}\nINPUT:\n" + "\n".join(sentences)
                + "\nOUTPUT:\n" + "\n".join(outputs) + "\n\n")

    # --- Summary ---
    c = totals["n"]
    print("\n--- SUMMARY ---")
    print(f"Model: {model_id}")
    print(f"Sentences: {c}")
    if c:
        print(f"Fidelity failures (fact/citation loss): {totals['fidelity_fail']}/{c}")
        print(f"Throughput: {c / totals['gen_s']:.2f} sent/sec ({totals['gen_s'] / c * 1000:.0f} ms/sentence)")
    print(f"\nAppended as section #{n} to: {path}")
    print("Next: paste the OUTPUT sentences into your ZeroGPT/GPTZero/Copyleaks step.")


if __name__ == "__main__":
    main()
