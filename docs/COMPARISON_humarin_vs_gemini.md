# Model Comparison: humarin T5 Paraphraser vs. Gemini 3.5 Flash-Lite

**Project:** ReviewIt Humanizer — rewriting AI-flagged sentences in research papers so they pass AI-content detectors without altering facts, citations, or meaning.
**Scope:** A head-to-head comparison of the two models evaluated to date for this task.
**Date:** 8 October 2026

---

## 1. Overview

Both models were assessed as sentence-level humanizers. A single AI-flagged sentence is rewritten, reinserted into its original (largely human-written) paragraph, and the reassembled text is submitted to AI-content detectors. Detectors used: **ZeroGPT** and **Copyleaks**.

The two models represent fundamentally different approaches:

- **humarin/chatgpt_paraphraser_on_T5_base** — a small, open-weight paraphrasing model run locally.
- **Gemini 3.5 Flash-Lite** — a commercial large language model accessed through Google's API and steered by prompt instructions.

---

## 2. Model profiles

| Attribute | humarin T5 Paraphraser | Gemini 3.5 Flash-Lite |
|---|---|---|
| Model type | T5 sequence-to-sequence paraphraser (not an LLM) | Instruction-following large language model (multimodal) |
| Parameters | ~223 million (open weights) | Not disclosed (proprietary) |
| Developer | Community (humarin) | Google |
| Operation | Fixed transformation; accepts a sentence and returns a paraphrase; no prompting | Prompt-driven; behaviour and constraints are set in the instruction |
| Deployment | Local, CPU, fully offline | Google Cloud API |
| Cost | Free (open model) | Free tier available (rate-limited); paid tier $0.30 per 1M input tokens, $2.50 per 1M output tokens |
| Throughput | ~0.45 sentences/second (CPU) | ~3 seconds per sentence (API) |
| Data handling | Nothing leaves the local machine | Text is sent to Google; free-tier inputs may be used for product improvement, paid-tier inputs are not |
| Reference | huggingface.co/humarin/chatgpt_paraphraser_on_T5_base | ai.google.dev/gemini-api/docs/models/gemini-3.5-flash-lite |

---

## 3. Test results

Each model was tested with the same procedure: rewrite the flagged sentence, reinsert it into the source paragraph, and score the reassembled text on the detectors.

| Criterion | humarin T5 Paraphraser | Gemini 3.5 Flash-Lite |
|---|---|---|
| Detection evasion (sentence reinserted into paragraph) | Passed — ZeroGPT 0%, Copyleaks 0% | Passed — ZeroGPT 0%, Copyleaks 0% |
| Fact, number, and citation preservation | Generally preserved, but cannot be enforced | Preserved, and enforceable via prompt rules and an automated check |
| Observed issue during testing | Altered meaning: "maximizing operational efficiency" became "driving down operational costs" | Inserted a citation not present in the source (traced to an example in the prompt); corrected, and the automated check now blocks added citations |
| Control over output | None; behaviour is fixed and cannot be instructed | Full; can be instructed to keep every citation and change no figure |
| Restyling capability | Synonym substitution only; retains the original formal structure | Genuine casual restyle, which is what reduces detector scores |

**Key observation:** At the sentence-reinsertion granularity used in production, both models reduced detector scores to 0%. Evasion alone therefore does not distinguish them. The distinguishing factor is **control over fidelity** — the ability to guarantee and verify that facts and citations are preserved.

---

## 4. Analysis

**humarin T5 Paraphraser** is fast, free, and private, and preserves content in straightforward cases. It is, however, a fixed model that cannot be steered: it performs synonym substitution only and retains the original sentence structure, and when it does change wording it can alter meaning with no mechanism to prevent it. For research papers, a fidelity risk that cannot be enforced is a material concern.

**Gemini 3.5 Flash-Lite** is an instruction-following model. It can be directed to restyle text while leaving every fact and citation unchanged, and that constraint can be verified automatically by the project's fidelity check, which flags any number or citation that is dropped or added. It incurs a per-call API cost and sends text to Google, but it is the only one of the two that combines genuine restyling with controllable, verifiable fidelity.

---

## 5. Notes and caveats

- Gemini's parameter count is not published; Google, like other providers of frontier commercial models, does not disclose it.
- Detector testing covered ZeroGPT and Copyleaks.
- Results reflect the product's intended use — rewriting a small number of flagged sentences within otherwise human-written text — not whole-document rewriting.
