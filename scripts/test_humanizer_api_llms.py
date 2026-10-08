"""
Test harness: commercial / general-purpose API LLMs for sentence-level humanization.
See docs/COMMERCIAL_LLM_RESEARCH.md for the full plan.

Providers supported (all API, prompted — no fine-tuning):
  gemini      gemini-3.8-flash         (google-genai SDK)   key: GEMINI_API_KEY
  deepseek    deepseek-flash           (OpenAI-compatible)  key: DEEPSEEK_API_KEY
  perplexity  sonar                    (OpenAI-compatible)  key: PERPLEXITY_API_KEY
  groq        qwen/qwen3.8-27b         (OpenAI-compatible)  key: GROQ_API_KEY   (current baseline)

What it does:
  - Runs a fixed set of AI-flagged academic sentences (or your own, one per line)
    through the chosen provider using 3 prompt variants (baseline / restyle+fact-lock / persona).
  - Logs per call: output text, thinking/reasoning tokens, output tokens, latency.
  - FIDELITY check: every number and in-text citation in the original must survive
    verbatim in the rewrite (flags any that don't).
  - Saves one combined file per prompt at data/<model>/<prompt>.txt; each run appends a
    numbered section (# 1, # 2, ...) with that run's INPUT and OUTPUT paragraphs.

It does NOT call any AI detector — feed the saved rewrites into your existing
ZeroGPT/GPTZero/Copyleaks step. Evasion scoring is deliberately kept separate.

Setup:
  1. pip install -r requirements.txt
  2. Put the relevant key(s) in .env  (free Gemini key: https://aistudio.google.com/apikey)
  3. python scripts/test_humanizer_api_llms.py [provider] [sentences_file]
       python scripts/test_humanizer_api_llms.py                      # gemini, built-in samples
       python scripts/test_humanizer_api_llms.py deepseek             # deepseek, built-in samples
       python scripts/test_humanizer_api_llms.py groq my_sents.txt    # groq, one sentence per line

Env / CLI overrides:
  LLM_PROVIDER   default provider if none given on CLI (default: gemini)
  LLM_MODEL      override the provider's default model (e.g. gemini-3.5-flash-lite)
  GEMINI_THINK   gemini only: low | medium | high  (3.8 Flash cannot go below 'low'; default low)
  LLM_PROMPTS    comma list of prompt variants to run (default: A).
                 Escalate only if A's detector score is poor, e.g. LLM_PROMPTS=B  or  B,C
"""

import os
import sys
import re
import time

from dotenv import load_dotenv
load_dotenv()

# --- Provider registry -------------------------------------------------------
PROVIDERS = {
    "gemini": {
        "kind": "gemini",
        "default_model": "gemini-3.8-flash",
        "key_env": "GEMINI_API_KEY",
    },
    "deepseek": {
        "kind": "openai",
        "default_model": "deepseek-flash",
        "key_env": "DEEPSEEK_API_KEY",
        "base_url": "https://api.deepseek.com",
    },
    "perplexity": {
        "kind": "openai",
        "default_model": "sonar",
        "key_env": "PERPLEXITY_API_KEY",
        "base_url": "https://api.perplexity.ai",
        "note": "search-augmented (RAG) - expect citation injection / fact drift; low priority",
    },
    "groq": {
        "kind": "openai",
        "default_model": "qwen/qwen3.8-27b",
        "key_env": "GROQ_API_KEY",
        "base_url": "https://api.groq.com/openai/v1",
    },
}

# --- Prompt variants ---------------------------------------------------------
# Each is (system_instruction, user_template). {s} is replaced by the sentence.
BANNED = "however, moreover, furthermore, thus, hence, consequently, thereby, nevertheless"

PROMPTS = {
    "A": (
        "You are a plain-language editor. Rewrite academic text into simple, everyday "
        "English that a non-expert would write.",
        "Rewrite this sentence in simple, everyday English.\n"
        "- Replace complex/academic words with the simplest everyday synonym.\n"
        "- Break it into shorter sentences (8-15 words).\n"
        f"- Do NOT use formal connectors: {BANNED}.\n"
        "- Keep all facts and every in-text citation exactly as written.\n"
        "- NEVER add a citation, reference, author name, or year that is not already "
        "in the sentence. Add no other new information.\n"
        "Return ONLY the rewrite.\n\nSentence:\n{s}",
    ),
    "B": (
        "You are a plain-language copy editor. Rewrite the given sentence as a tired grad "
        "student would explain it to a friend - casual, direct, uneven.",
        "Rewrite the sentence.\n"
        "- Swap every academic word for the simplest everyday one.\n"
        "- Break it into 2-3 short sentences of uneven length (some 4-6 words, some 12-15) "
        "- vary the rhythm.\n"
        "- You may start with \"And\" or \"But\".\n"
        f"- Never use: {BANNED}.\n"
        "- Keep every number, statistic, and in-text citation EXACTLY as written - "
        "do not add, remove, or reword any citation or figure.\n"
        "- NEVER introduce a citation or reference that was not already in the sentence.\n"
        "- Add no new information. Output only the rewrite.\n\nSentence:\n{s}",
    ),
    "C": (
        "You rewrite academic sentences in the voice of a specific person: a sleep-deprived "
        "second-year PhD student venting to a labmate. Blunt, plain, a little ragged.",
        "Rewrite the sentence in that voice.\n"
        "- Deliberate burstiness: mix short fragments with one longer clause.\n"
        "- Everyday words only; no academic register.\n"
        f"- Never use: {BANNED}.\n"
        "- Keep every number, statistic, and in-text citation EXACTLY as written. "
        "NEVER add a citation or reference that was not already there. Add no new information.\n"
        "Output only the rewrite.\n\nSentence:\n{s}",
    ),
}

# --- Built-in test set (AI-flagged academic sentences, 10-40 words) ----------
# Chosen to stress numbers, stats, and citations - the fact-preservation risk.
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

# --- Fidelity checking -------------------------------------------------------
NUM_RE = re.compile(r"\b\d[\d,]*\.?\d*%?\b")
# Citations, three common forms:
#   [14]                                           numeric
#   Chen et al. (2021) / Smith and Jones (2019)    narrative (author outside parens)
#   (Smith & Jones, 2019) / (2019)                 parenthetical (year inside parens)
CITE_RE = re.compile(
    r"\[\d+\]"
    r"|[A-Z][A-Za-z]+(?:\s+(?:et al\.?|&\s*[A-Z][A-Za-z]+|and\s+[A-Z][A-Za-z]+))?\s*\(\d{4}[a-z]?\)"
    r"|\([^()]*?\b\d{4}[a-z]?\b[^()]*?\)"
)


def _norm_numbers(text):
    """Normalize number formats so '27 percent'=='27%' and '1,482'=='1482'."""
    t = text.lower().replace("percent", "%")
    t = re.sub(r"(\d)\s*%", r"\1%", t)        # "27 %" -> "27%"
    t = re.sub(r"(?<=\d),(?=\d)", "", t)       # "1,482" -> "1482"
    return t


def extract_facts(text):
    nums = set(NUM_RE.findall(_norm_numbers(text)))
    cites = set(c.strip() for c in CITE_RE.findall(text))
    return nums, cites


def fidelity_check(original, rewrite):
    """Return (ok, missing_nums, added_nums, missing_cites, added_cites).

    Catches BOTH dropped facts (missing) and hallucinated ones (added). An added
    citation is a fabricated reference - the key failure mode for research papers.
    """
    o_nums, o_cites = extract_facts(original)
    r_nums, r_cites = extract_facts(rewrite)
    missing_nums = sorted(o_nums - r_nums)
    added_nums = sorted(r_nums - o_nums)
    missing_cites = sorted(o_cites - r_cites)
    added_cites = sorted(r_cites - o_cites)
    ok = not (missing_nums or added_nums or missing_cites or added_cites)
    return ok, missing_nums, added_nums, missing_cites, added_cites


# --- Provider clients --------------------------------------------------------
GEMINI_THINK = os.environ.get("GEMINI_THINK", "low")


def make_client(provider, cfg, api_key):
    if cfg["kind"] == "gemini":
        from google import genai
        return genai.Client(api_key=api_key)
    else:  # openai-compatible
        from openai import OpenAI
        return OpenAI(api_key=api_key, base_url=cfg["base_url"])


def _gemini_config(system_instruction):
    """Build GenerateContentConfig, degrading gracefully if the installed SDK
    doesn't expose thinking_level (field name is mid-migration in google-genai)."""
    from google.genai import types
    base = dict(
        system_instruction=system_instruction,
        temperature=1.0,
        # We pass no tools; disabling AFC silences the SDK's "not recommended" warning.
        automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
    )
    for thinking in (
        lambda: types.ThinkingConfig(thinking_level=GEMINI_THINK),
        lambda: types.ThinkingConfig(thinking_budget=0),
        None,
    ):
        try:
            if thinking is None:
                return types.GenerateContentConfig(**base)
            return types.GenerateContentConfig(thinking_config=thinking(), **base)
        except (TypeError, ValueError):
            continue
    return types.GenerateContentConfig(**base)


def call_llm(provider, cfg, client, model, system_instruction, user_text):
    """Return normalized dict regardless of provider."""
    for attempt in range(5):
        try:
            t0 = time.time()
            if cfg["kind"] == "gemini":
                resp = client.models.generate_content(
                    model=model, contents=user_text,
                    config=_gemini_config(system_instruction),
                )
                latency = time.time() - t0
                u = resp.usage_metadata
                return {
                    "text": (resp.text or "").strip(),
                    "latency_s": round(latency, 2),
                    "prompt_tokens": getattr(u, "prompt_token_count", None),
                    "thinking_tokens": getattr(u, "thoughts_token_count", None),
                    "output_tokens": getattr(u, "candidates_token_count", None),
                    "error": None,
                }
            else:  # openai-compatible
                resp = client.chat.completions.create(
                    model=model, temperature=1.0,
                    messages=[
                        {"role": "system", "content": system_instruction},
                        {"role": "user", "content": user_text},
                    ],
                )
                latency = time.time() - t0
                u = resp.usage
                details = getattr(u, "completion_tokens_details", None)
                return {
                    "text": (resp.choices[0].message.content or "").strip(),
                    "latency_s": round(latency, 2),
                    "prompt_tokens": getattr(u, "prompt_tokens", None),
                    "thinking_tokens": getattr(details, "reasoning_tokens", None),
                    "output_tokens": getattr(u, "completion_tokens", None),
                    "error": None,
                }
        except Exception as e:
            err = str(e)
            if "429" in err or "RESOURCE_EXHAUSTED" in err or "rate" in err.lower():
                m = re.search(r"(\d+(?:\.\d+)?)\s*s", err)
                wait = (float(m.group(1)) + 2) if m else 30
                print(f"    rate limit - waiting {wait:.0f}s...")
                time.sleep(wait)
            else:
                return {"text": "", "latency_s": None, "prompt_tokens": None,
                        "thinking_tokens": None, "output_tokens": None, "error": err}
    return {"text": "", "latency_s": None, "prompt_tokens": None,
            "thinking_tokens": None, "output_tokens": None, "error": "failed after retries"}


# --- CLI / main --------------------------------------------------------------
def parse_args():
    args = sys.argv[1:]
    provider = None
    if args and args[0] in PROVIDERS:
        provider = args.pop(0)
    elif args and not os.path.exists(args[0]):
        # First arg is neither a known provider nor an existing file - likely a typo.
        print(f"'{args[0]}' is not a known provider or an existing file.\n"
              f"Providers: {', '.join(PROVIDERS)}")
        sys.exit(1)
    provider = provider or os.environ.get("LLM_PROVIDER", "gemini")
    if provider not in PROVIDERS:
        print(f"Unknown provider '{provider}'. Choose one of: {', '.join(PROVIDERS)}")
        sys.exit(1)
    sentences_file = args[0] if args else None
    return provider, sentences_file


def load_sentences(sentences_file):
    if sentences_file:
        with open(sentences_file, "r", encoding="utf-8") as f:
            lines = [ln.strip() for ln in f if ln.strip()]
        print(f"Loaded {len(lines)} sentences from {sentences_file}")
        return lines
    print(f"Using {len(SAMPLE_SENTENCES)} built-in sample sentences")
    return SAMPLE_SENTENCES


def main():
    provider, sentences_file = parse_args()
    cfg = PROVIDERS[provider]
    model = os.environ.get("LLM_MODEL", cfg["default_model"])
    api_key = os.environ.get(cfg["key_env"])
    if not api_key:
        print(f"{cfg['key_env']} not set. Add it to .env")
        if provider == "gemini":
            print("  Free Gemini key: https://aistudio.google.com/apikey")
        sys.exit(1)

    variants = [p.strip().upper() for p in os.environ.get("LLM_PROMPTS", "A").split(",")]
    variants = [v for v in variants if v in PROMPTS]
    sentences = load_sentences(sentences_file)

    print(f"Provider: {provider} | model: {model}"
          + (f" | thinking: {GEMINI_THINK}" if cfg["kind"] == "gemini" else "")
          + f" | prompts: {','.join(variants)}")
    if cfg.get("note"):
        print(f"NOTE: {cfg['note']}")
    print()

    client = make_client(provider, cfg, api_key)

    results = []
    totals = {"calls": 0, "thinking_tokens": 0, "output_tokens": 0,
              "fidelity_fail": 0, "latency_s": 0.0}

    for i, sent in enumerate(sentences, 1):
        print(f"[{i}/{len(sentences)}] {sent[:70]}...")
        for v in variants:
            sys_inst, user_tmpl = PROMPTS[v]
            out = call_llm(provider, cfg, client, model, sys_inst, user_tmpl.format(s=sent))
            if out["error"]:
                print(f"  {v}: ERROR {out['error'][:90]}")
                continue
            ok, miss_n, add_n, miss_c, add_c = fidelity_check(sent, out["text"])
            totals["calls"] += 1
            totals["thinking_tokens"] += out["thinking_tokens"] or 0
            totals["output_tokens"] += out["output_tokens"] or 0
            totals["latency_s"] += out["latency_s"] or 0
            if not ok:
                totals["fidelity_fail"] += 1
            flag = "OK " if ok else "FACT-LOSS"
            print(f"  {v}: [{flag}] think={out['thinking_tokens']} out={out['output_tokens']} "
                  f"{out['latency_s']}s -> {out['text'][:70]}")
            if miss_n:
                print(f"       missing numbers: {miss_n}")
            if add_n:
                print(f"       ADDED numbers (hallucination?): {add_n}")
            if miss_c:
                print(f"       missing citations: {miss_c}")
            if add_c:
                print(f"       ADDED citations (fabricated reference!): {add_c}")
            results.append({
                "provider": provider, "model": model, "sentence_index": i,
                "prompt": v, "original": sent, "rewrite": out["text"],
                "fidelity_ok": ok, "missing_numbers": miss_n, "added_numbers": add_n,
                "missing_citations": miss_c, "added_citations": add_c,
                **{k: out[k] for k in ("latency_s", "prompt_tokens",
                                       "thinking_tokens", "output_tokens")},
            })
        time.sleep(1)  # gentle on free-tier RPM; raise if you hit 429s

    # --- Save ---
    #   data/<model>/inputs/input_<prompt>_<n>.txt
    #   data/<model>/outputs/output_<prompt>_<n>.txt
    # Both files are paragraph form (sentences joined in order). <n> is a run counter
    # that continues from the highest existing index in the model's outputs folder.
    model_dir = os.path.normpath(os.path.join(
        os.path.dirname(__file__), "..", "data", model.replace("/", "-")))
    os.makedirs(model_dir, exist_ok=True)

    def next_section(path):
        """Next run number for a prompt file: highest existing '# N' heading + 1."""
        if not os.path.exists(path):
            return 1
        with open(path, "r", encoding="utf-8") as f:
            nums = [int(m.group(1)) for m in re.finditer(r"(?m)^# (\d+)\s*$", f.read())]
        return (max(nums) + 1) if nums else 1

    input_paragraph = " ".join(sentences)
    run_outputs = []
    for v in variants:
        rewrites = [r["rewrite"] for r in sorted(
            (r for r in results if r["prompt"] == v),
            key=lambda r: r["sentence_index"]) if r["rewrite"]]
        if not rewrites:
            continue
        output_paragraph = " ".join(rewrites)
        path = os.path.join(model_dir, f"{v}.txt")          # one combined file per prompt
        n = next_section(path)
        with open(path, "a", encoding="utf-8") as f:        # append a numbered section
            f.write(f"# {n}\nINPUT:\n{input_paragraph}\nOUTPUT:\n{output_paragraph}\n\n")
        run_outputs.append((v, n, path, output_paragraph))

    # --- Summary ---
    c = totals["calls"]
    print("\n--- SUMMARY ---")
    print(f"Provider/model: {provider} / {model}")
    print(f"Calls: {c}")
    if c:
        print(f"Fidelity failures (fact/citation loss): {totals['fidelity_fail']}/{c}")
        print(f"Avg thinking tokens/call: {totals['thinking_tokens'] / c:.0f}")
        print(f"Avg output tokens/call:   {totals['output_tokens'] / c:.0f}")
        print(f"Avg latency/call:         {totals['latency_s'] / c:.2f}s")
    for v, n_idx, out_path, output_paragraph in run_outputs:
        print(f"\n--- OUTPUT PARAGRAPH (prompt {v}, section #{n_idx}) ---")
        print(output_paragraph)
        print(f"appended as section #{n_idx} to: {out_path}")

    print("\nNext: paste output.txt into your ZeroGPT/GPTZero/Copyleaks step.")


if __name__ == "__main__":
    main()
