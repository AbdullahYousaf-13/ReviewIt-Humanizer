# Detection-Evasion Models Research — ReviewIt Humanizer

> **Scope:** DL models/frameworks **specifically built to evade AI-text detectors** (humanize
> AI text), 2023–2026. These differ from general paraphrasers (which only swap synonyms and
> fail — see [MODEL_RESEARCH.md](MODEL_RESEARCH.md)) and from general-purpose LLMs
> (see [LLM_RESEARCH.md](LLM_RESEARCH.md)). Target detectors for this project:
> **ZeroGPT, Copyleaks, GPTZero.**

**Key pattern (2026):** the *effective* new evaders are **small non-LLM models trained with
multi-stage pipelines** (SFT → preference optimization → refinement), and they generally
**release code/recipes, not weights** — you train your own. The ones that *do* release
weights are LLMs with only modest evasion. Meanwhile **Turnitin's 2025/2026 updates were
retrained to catch humanizer output** (60–80% detection on popular tools) — it's a treadmill.

---

## ⭐ MASH — Multi-stage Alignment for Style Humanization (ACL Findings 2026)

**The best architectural fit for this project.** Small, non-LLM, purpose-built, strong
reported evasion, cheap to train, CPU-friendly inference.

| Spec | Value |
|---|---|
| Base model | **facebook/bart-base (~0.1B / 140M)** — seq2seq, non-LLM |
| Technique | 4-stage: data construction → style-injection SFT → DPO → inference refinement |
| Reported evasion | **92% avg ASR** across 6 datasets, 5 detectors |
| Semantic preservation | BERTScore ~0.89–0.90 (decent; **no explicit fact/citation guarantee**) |
| Training cost | **1× RTX 3090 (24 GB), ~7.5 h per domain** — cheap |
| Inference | ~3.1 GB, 1.7 s/sample — **CPU-feasible once trained** |
| Weights | ❌ **Not released** — training code only (research-only license) |
| Links | [Paper](https://arxiv.org/html/2601.08564) · [GitHub](https://github.com/githigher/MASH) |

### Pipeline (4 stages)

1. **Data construction** — build ~6,000 AI↔human parallel pairs from open datasets
   (`dmitva/human_ai_generated_text`), filtered by a detector. JSONL with `src` (AI) / `trg`
   (human) fields. ~95% label-flip success.
2. **Style-injection SFT** — train BART-base with trainable AI-style & human-style embeddings;
   joint reconstruction + transformation loss (λ=0.5) to shift style while keeping meaning.
3. **DPO alignment** — Direct Preference Optimization using **a detector's confidence as the
   reward** (hard-negative mining on SFT outputs that fail evasion).
4. **Inference-time refinement** — split into sentences, polish candidates with **GPT-4**,
   rank by perplexity, keep a swap only if it stays classified "human."

### Detectors tested (and the gap)

- Open-source: RoBERTa ~87%, Binoculars ~91%, SCRN (similar)
- Commercial: **Writer API ~89%, Scribbr API ~88%**
- ❌ **NOT tested: ZeroGPT, GPTZero, Copyleaks, Originality, Turnitin** — i.e. none of *our*
  three targets. Stage 3 trains against whatever detector is plugged in, so beating our
  targets means putting **them** in the DPO loop (their APIs → cost/rate-limits).

### Catches for us

1. **No weights → must train it** (needs a 24 GB GPU; Colab Pro L4/A100 or rented).
2. **Our 3 detectors unproven** — would need to DPO-train against them specifically.
3. **Stage 4 uses GPT-4** (an LLM API at inference) — can be skipped/swapped, losing some quality.
4. **No fact/citation preservation mechanism** — relies on BERTScore ~0.9; bolt on our own
   number/citation checker for research papers.
5. Research-only license; English only; adversarial-trained detectors reduce ASR to ~0.

### Verdict

Most achievable "build your own" path: 140M model, ~7.5 GPU-hours/domain, reproducible recipe,
reportedly beats some commercial detectors. The work: source data, train Stage 3 against our
actual detectors, handle Stage 4 without GPT-4, and add fact-preservation.

---

## GradEscape — Gradient-Based Evader (USENIX Security 2025)

| Spec | Value |
|---|---|
| Model | **139M param evader**, gradient-based (weighted-embedding trick for discrete text) |
| Results | Outperforms an 11B paraphraser; **applied to 2 real commercial detectors** |
| Catch | It's an *attack framework* — needs access to the victim detector to train the evader |
| Weights | Open-sourced (code) for building more robust detectors |
| Link | [Paper + code](https://arxiv.org/abs/2506.08188) |

---

## jialinyyzz/humanizer — released weights, but an LLM (2026)

| Spec | Value |
|---|---|
| Base | Gemma-based (**~4–12B — an LLM**) |
| Training | SFT + DPO + GRPO, **no detector in the reward** (detector-agnostic) |
| Weights | ✅ **Released** (GGUF Q8/Q6, bf16) — runs locally |
| Results | Originality.ai 57% → **85% human** (modest; tested once, not in training) |
| Facts | Fact-aware (0/62 critical errors v2) but **drops qualifiers ~1 in 3 outputs** |
| Catch | It's an LLM (ruled out); modest evasion; untested on ZeroGPT/GPTZero/Copyleaks |
| Links | [Model](https://huggingface.co/jialinyyzz/humanizer) · [Blog](https://huggingface.co/blog/jialinyyzz/we-built-an-ai-humanizer-and-never-let-it-see-a-de) |

---

## CoPA — Contrastive Paraphrase Attack (EMNLP 2025)

| Spec | Value |
|---|---|
| Technique | **Training-free** — uses off-the-shelf LLMs with contrastive/proxy guidance |
| Catch | LLM-based; proxy guidance may miss target-specific decision boundaries |
| Link | [Paper](https://arxiv.org/pdf/2505.15337) |

---

## Also researched (details in other files)

| Model | Where | Note |
|---|---|---|
| AuthorMist (Qwen2.5-3B, RL) | [LLM_RESEARCH.md](LLM_RESEARCH.md) | LLM; weights not released |
| StealthRL (Qwen3-4B + LoRA, RL) | [LLM_RESEARCH.md](LLM_RESEARCH.md) | LLM; targets academic detectors |
| DIPPER (T5-XXL 11B) | [MODEL_RESEARCH.md](MODEL_RESEARCH.md) | Large seq2seq; stale vs modern detectors |

---

## Summary ranking (for our constraints: non-LLM, CPU, targets = ZeroGPT/Copyleaks/GPTZero)

| Model | Non-LLM? | Weights? | Evasion | Fit |
|---|---|---|---|---|
| **MASH** | ✅ 140M BART | ❌ train it | 92% (not our detectors) | ⭐ best — but build-it-yourself + GPU to train |
| GradEscape | ✅ 139M | code only | strong (commercial) | attack framework, needs detector access |
| jialinyyzz/humanizer | ❌ LLM | ✅ yes | modest (85% human) | ready but LLM + weak |
| CoPA | ❌ LLM | training-free | moderate | LLM-based |
