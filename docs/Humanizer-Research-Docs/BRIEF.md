# Project Brief — Research Paper Humanizer

## Goal
Rewrite AI-flagged sentences in a research paper so it passes AI detectors — **without changing any fact, number, citation, or meaning**. Targets: **ZeroGPT, Copyleaks, GPTZero**.

## Pipeline
An upstream tool flags AI sentences → we rewrite **only those** → reinsert into the paper. Unit = one sentence (10–40 words). Detectors score the whole passage, so a few rewritten sentences inside mostly-human text is the easy case.

## Key finding — evasion is easy, fidelity is hard (2026-10-08)
At the product's real granularity (rewrite flagged sentences, reinsert), the paper reliably hits **0% on ZeroGPT and Copyleaks** — with LLMs, humarin, and even PEGASUS. The detector score no longer separates methods; the deciding metric is **fidelity** (keep every fact/citation/meaning).

| Method | Evasion (reinsert) | Fidelity |
|---|---|---|
| LLM (Gemini, prompted) | ✅ 0% | ✅ best — can **enforce** "keep facts/citations" + auto-check |
| humarin | ✅ 0% | ⚠️ drifts, no control ("efficiency" → "costs") |
| PEGASUS | ✅ 0% | ❌ deletes content |
| BART | ❌ (copies input) | ✅ faithful but no change |

Only LLM prompting both restyles **and** lets you command + verify fact preservation; paraphraser models can't be constrained. Details: [COMMERCIAL_LLM_RESEARCH.md](COMMERCIAL_LLM_RESEARCH.md), [MODEL_RESEARCH.md](MODEL_RESEARCH.md).

## Approaches (no winner chosen)
| Approach | Script | Result | Doc |
|---|---|---|---|
| Commercial API LLMs (prompted) | `test_humanizer_api_llms.py` | 0% ZeroGPT+Copyleaks; fact rules enforceable | [COMMERCIAL_LLM_RESEARCH.md](COMMERCIAL_LLM_RESEARCH.md) |
| Qwen via Groq (paragraph-level) | `test_humanizer_llm.py` | aggressive restyle evades | [LLM_RESEARCH.md](LLM_RESEARCH.md) |
| Local paraphrasers (humarin/BART/PEGASUS) | `test_humanizer_models.py` | evade in context but fidelity uncontrollable | [MODEL_RESEARCH.md](MODEL_RESEARCH.md) |

## Hard constraints
- No hallucination — every fact/number comes from the original.
- Never add, drop, or alter a citation. **Adding a fake citation is as bad as dropping one.**
- Add no new content; keep technical terms as-is.

## What moves detector scores
Casual **restyle**, not synonym-swapping: simple everyday words, short sentences (8–15 words), varied length, occasional "And/But", no formal connectors (however, furthermore, …). Faithful paraphrasing alone does NOT evade.

## Prompts (API harness, default A)
Keep every number/citation exactly; **never add a citation/author/year not already present**; no new info. Variants: A plain restyle, B aggressive + fact-lock, C persona/burstiness. Full prompts in [COMMERCIAL_LLM_RESEARCH.md](COMMERCIAL_LLM_RESEARCH.md).
⚠️ Never put a real-looking example citation in a prompt — the model copies it out as a fake reference (bug found & fixed).

## Known issues
- All-AI blocks only partially evade (38.7%); relies on flagged sentences being sparse in human text.
- `gemini-3.8-flash` is slow (~48s/sentence, reasoning) → default is `gemini-3.5-flash-lite`.
- Groq free tier: hidden OTPM≈1,000 → throttling. Gemini free tier: per-account requests/day cap.

## Not decided
- Which method/model to ship.
- How the upstream tool flags/passes sentences.
- Not yet validated on GPTZero; Copyleaks tested only at sensitivity 2/3.
