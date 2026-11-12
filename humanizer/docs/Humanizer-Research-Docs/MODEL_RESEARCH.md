# Model Research (Non-LLM) — ReviewIt Humanizer

> Non-LLM seq2seq models for sentence-level rewriting (paraphrase / style-transfer / simplification) and dedicated evasion models. LLMs → [LLM_RESEARCH.md](LLM_RESEARCH.md). Run via `scripts/test_humanizer_models.py` (CPU, offline).

## Sentence-level re-test (2026-10-08) — fidelity is the differentiator
At the product's granularity (rewrite flagged sentences, reinsert), all of these clear detection — so the detector score no longer discriminates; **fidelity** does. (On their own / whole-text they still score ~100% AI.)

| Model | Evasion (reinsert) | Fidelity |
|---|---|---|
| humarin (T5, 223M) | ✅ Copyleaks 0% | ⚠️ drifts — "maximizing efficiency" → "driving down costs" (no control) |
| PEGASUS (569M) | ✅ Copyleaks 0% | ❌ deletes content — dropped 3/4 list items |
| BART (eugenesiow, 406M) | ❌ returns input ~verbatim | ✅ faithful but no change |

None is reliable: paraphrasers can't be *constrained* to preserve facts (no prompts). Only LLM prompting can — see [COMMERCIAL_LLM_RESEARCH.md](COMMERCIAL_LLM_RESEARCH.md).

### Model facts (checked 2026-11-12; all models on one page: [MODELS.md](../../../MODELS.md))
| Model | Parameters | Weights | Licence |
|---|---|---|---|
| humarin/chatgpt_paraphraser_on_T5_base | 222.9M | 0.89 GB | OpenRAIL |
| Vamsi/T5_Paraphrase_Paws (second tier in the app) | 222.9M | 0.89 GB | not stated |
| tuner007/pegasus_paraphrase | 569M | 2.28 GB | Apache 2.0 |
| eugenesiow/bart-paraphrase | 406M | 1.63 GB | Apache 2.0 |
| Nubletz/bart-text-simplification | 406M | 1.63 GB | not stated |
| followsci/bert-ai-text-detector (the detector) | 109.5M | 0.44 GB | MIT |

### Model notes
- **humarin/chatgpt_paraphraser_on_T5_base** — conservative synonym swaps, keeps formal structure. On its own: ZeroGPT 100% → 100%.
- **eugenesiow/bart-paraphrase** — even more conservative; returns sentences ~verbatim.
- **tuner007/pegasus_paraphrase** — summarizer; drops clauses (removes info). `embed_positions` re-inits under transformers 5.x but output is still coherent.

## Candidates
| Model | Class | Status |
|---|---|---|
| Styleformer `prithivida/formal_to_informal_styletransfer` | T5 style transfer (a **model**, not an LLM) | ⏳ parked — trained on social text (too informal; may mangle terms/citations) |
| `Nubletz/bart-text-simplification` | BART simplification (ASSET+TurkCorpus) | ❌ **broken** — tokenizer vs config token-id mismatch (tokenizer bos=2/eos=3/pad=0 vs config bos=0/decoder_start=2) → output decodes to empty under every decoding setting. Unusable as uploaded. |
| DIPPER `kalpeshk2011/dipper-paraphraser-xxl` | T5-XXL 11B paraphraser | ❌ ruled out — 11B, can't run on CPU; stale vs modern detectors (2025 TH-Bench) |

> Dedicated evasion models (MASH, GradEscape, …) → [EVASION_MODELS_RESEARCH.md](EVASION_MODELS_RESEARCH.md). RL evasion LLMs (AuthorMist, StealthRL) → [LLM_RESEARCH.md](LLM_RESEARCH.md).
>
> Research note: purpose-built non-LLM humanizers still only *partially* evade retrained classifiers (e.g. arXiv 2506.12843 cut detector accuracy ~19%, output "insufficiently human-like").
