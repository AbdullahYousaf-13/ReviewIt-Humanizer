# Model Research (Non-LLM) — ReviewIt Humanizer

> **Scope:** Non-LLM models for sentence-level paraphrasing / style transfer / AI-detection
> evasion — seq2seq paraphrasers, style-transfer, simplification, and dedicated evasion
> models. For the general-purpose instruction LLMs tried in the pipeline (Qwen, GPT-OSS,
> Llama via Groq), see [LLM_RESEARCH.md](LLM_RESEARCH.md).

---

## A. Tested locally

Run via `scripts/test_humanizer_models.py` on CPU in the project `.venv`. Small seq2seq
paraphrasers that run offline (no API, no rate limits). The per-model "FAILS EVASION" verdicts
below are the **on-their-own / whole-text** ZeroGPT results. For the **product's real
granularity** — rewrite only the flagged sentences and reinsert into the mostly-human paper —
see the sentence-level re-test next.

### ⭐ Sentence-level re-test (2026-10-08, new harness) — evasion is the easy part

Tested the actual product pipeline: humanize only the flagged sentence(s), reinsert, score the
reassembled paragraph on **Copyleaks** (strict, sensitivity 2/3).

| Model | Reinsert → detector | Fidelity (the real differentiator) |
|---|---|---|
| **humarin** | ✅ Copyleaks 0% | ⚠️ paraphrases but **no control** — drifted "maximizing operational efficiency" → "driving down operational costs" |
| **PEGASUS** | ✅ Copyleaks 0% | ❌ **deletes content** — dropped 3 of 4 list items ("aggregation, coding, long-term preservation") |
| **BART** | — (returns input ~verbatim) | ✅ faithful but no change → pointless |

**Key reframe:** at the product's sentence-level granularity (rewrite flagged sentences, reinsert),
the reassembled paper reliably passes detection with *any* of these — so the **detector score no
longer discriminates between methods.** Evasion is the easy part. The deciding metric is
**fidelity**: keep every fact, number, citation, and the exact meaning. The paraphrasers can't be
*constrained* (no prompts), so they drift (humarin) or delete (PEGASUS). Only the LLM-prompting
path lets you enforce "don't touch facts/citations" and auto-check it
(see [LLM_RESEARCH.md](LLM_RESEARCH.md) and COMMERCIAL_LLM_RESEARCH.md).

### `humarin/chatgpt_paraphraser_on_T5_base` — ❌ FAILS EVASION

| Spec | Value |
|---|---|
| Base | google-t5/t5-base |
| Size | 223M params |
| License | OpenRAIL |
| Training data | Quora + SQuAD 2.0 + CNN news paraphrase pairs |
| Speed (CPU) | ~0.45 sent/sec short; ~10s on a full paragraph |
| Facts/citations | ✅ Preserved perfectly (23.4%, 0.91, citations intact) |
| **Evasion** | ❌ **ZeroGPT 100% AI → 100% AI (confirmed)** |
| Link | https://huggingface.co/humarin/chatgpt_paraphraser_on_T5_base |

Conservative synonym swaps only ("transformative"→"paradigm", "simulate"→"imitate").
Structure/length/register untouched — exactly what detectors read.

### `eugenesiow/bart-paraphrase` — ❌ FAILS EVASION

| Spec | Value |
|---|---|
| Base | facebook/bart-large |
| Size | 406M params |
| License | Apache 2.0 |
| Speed (CPU) | ~0.17 sent/sec sentence-by-sentence (~6s/sentence) |
| Facts/citations | ✅ Preserved when fed one sentence per line (auto-split fixes the earlier content-loss) |
| **Evasion** | ❌ **ZeroGPT 100% AI → 100% AI (confirmed)** |
| Link | https://huggingface.co/eugenesiow/bart-paraphrase |

Even more conservative than humarin — 2 of 3 sentences returned **verbatim**. Safe for facts,
useless for evasion. (On whole-paragraph input it also truncates/drops content; feed
one sentence per line.)

### `tuner007/pegasus_paraphrase` — ❌ FAILS (summarizer — drops content)

| Spec | Value |
|---|---|
| Base | PEGASUS (google/pegasus) |
| Size | 569M params |
| Speed (CPU) | ~0.12 sent/sec (~8.7s/sentence) |
| Facts/citations | ❌ Drops clauses (summarization model) — removes information |
| **Evasion** | Not viable — content loss disqualifies it before detector testing |
| Note | `embed_positions` weights re-init under current transformers (quality risk) |
| Link | https://huggingface.co/tuner007/pegasus_paraphrase |

### Conclusion on faithful paraphrasers

**On their own, humarin, bart, and pegasus all fail evasion** — they keep the formal structure
detectors key on (humarin, bart) or lose content (bart on long input, pegasus). But at the
product's **sentence-level reinsertion** granularity they all clear detection (see the re-test
above), which makes **fidelity — not evasion — the selection criterion.** On fidelity they rank
humarin > pegasus > bart, yet **none is reliable**: there's no way to *enforce* fact/citation
preservation, so humarin drifted a claim and pegasus deleted content. Faithful paraphrasing ≠
controllable humanization. The only method that both restyles and lets you lock facts/citations
is LLM prompting.

---

## B. Non-LLM candidates — NOT yet tested (the forward path)

These change register/structure rather than preserving it, so they have a real mechanism for
evasion. Still CPU-runnable seq2seq.

### `Styleformer` (formal → casual style transfer) — ⏳ PARKED

| Spec | Value |
|---|---|
| Author | prithivida (Prithiviraj Damodaran) |
| Base | **T5-based seq2seq (a model, NOT an LLM)** — same class as humarin |
| Task | Formal ↔ casual, active ↔ passive style transfer (no prompting) |
| Formal→casual model | ✅ `prithivida/formal_to_informal_styletransfer` (verified exists; via the `styleformer` lib, `Styleformer(style=1)`) |
| Why it fits | Casual restyle directly attacks the "formal AI prose" signal (matches BRIEF.md) |
| Why parked | Trained on **everyday/social text** (slang, "hehe..", lowercase) — likely too informal for academic prose and may mangle technical terms/citations |
| Links | GitHub: https://github.com/PrithivirajDamodaran/Styleformer |

### `Nubletz/bart-text-simplification` — ⏳ NEXT TO TEST (id verified)

| Spec | Value |
|---|---|
| Base | facebook/bart-large-cnn, fine-tuned on ASSET + TurkCorpus |
| Task | Sentence simplification (shorter, simpler structure) |
| Risk | Simplification may drop nuance/detail — watch fact preservation (same failure mode as PEGASUS) |
| Run | No code change needed — pass the full id to the harness: `python scripts/test_humanizer_models.py Nubletz/bart-text-simplification <file>` → saves to `data/bart-text-simplification/output.txt` |
| Link | https://huggingface.co/Nubletz/bart-text-simplification |

**Expectation (from research):** Even purpose-built non-LLM humanizers only *partially* evade.
[*Transforming Chatbot Text: A Seq2Seq Approach* (arXiv 2506.12843)](https://arxiv.org/pdf/2506.12843)
fine-tuned T5-small/BART on GPT→human pairs and cut detector accuracy by **~19%**, but the
output was *"insufficiently human-like to evade retrained classifiers."*

---

## C. Large dedicated paraphraser (researched — ruled out)

Strong evasion in its original paper, but doesn't fit the constraints (CPU-only; 11B).

> **Note:** The RL-based evasion models **AuthorMist** and **StealthRL** used to be listed
> here but were moved to [LLM_RESEARCH.md](LLM_RESEARCH.md) — they are **LLMs** (Qwen 3B/4B
> decoder-only), not seq2seq models. DIPPER stays here as a large seq2seq paraphraser.

### DIPPER — `kalpeshk2011/dipper-paraphraser-xxl`

| Spec | Value |
|---|---|
| Base | T5-XXL (seq2seq), fine-tuned on 6.3M paraphrase pairs |
| Size | **11B params** |
| Evasion (2023) | Dropped DetectGPT 70.3% → 4.6% |
| Caveat | 2025 TH-Bench: now **poor vs modern model-based detectors** (sometimes raises AUC) |
| Fit | ❌ 11B — impractical on CPU; designed for paragraphs-with-context, not isolated sentences |
| Links | Paper: https://arxiv.org/pdf/2303.13408 · HF: https://huggingface.co/kalpeshk2011/dipper-paraphraser-xxl |

---

## Overall status

**Evasion** below = **sentence-level reinsertion** (the product scenario: rewrite only the flagged
sentences, reinsert, score the paragraph on Copyleaks). On their own / whole-text, the faithful
paraphrasers still score ~100% AI. **Fidelity** is the real differentiator.

| Model | Class | Fidelity | Evasion (reinsert) |
|---|---|---|---|
| humarin T5 | Faithful paraphraser | ⚠️ CPU; **drifts** (no control — "efficiency"→"costs") | ✅ **0% (Copyleaks)** |
| pegasus | Summarizer | ❌ **deletes content** (dropped list items) | ✅ **0% (Copyleaks)** |
| bart-paraphrase | Faithful paraphraser | ✅ CPU, faithful | ❌ none — returns input ~verbatim |
| Styleformer (T5, not an LLM) | Style transfer | ✅ CPU | ⏳ parked — trained on social text (too informal) |
| bart-text-simplification | Simplification | ⚠️ may drop detail | ⏳ **next to test** (id verified) |
| DIPPER | Large paraphraser | ❌ 11B | ❌ ruled out — CPU can't run 11B; stale vs modern detectors |

> humarin and PEGASUS **do evade** at sentence-level reinsertion (0% Copyleaks) — but that's true of
> almost any rewrite in context, so the deciding factor is fidelity, where both fail to be
> *controllable* (humarin drifts meaning, PEGASUS deletes content). BART changes nothing, so it
> doesn't evade even in context. LLM-based evasion models (AuthorMist, StealthRL) are in
> [LLM_RESEARCH.md](LLM_RESEARCH.md).
