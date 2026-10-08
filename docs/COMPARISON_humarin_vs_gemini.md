# Model Comparison — humarin T5 Paraphraser vs Gemini 3.5 Flash-Lite

**Project:** ReviewIt Humanizer (rewrite AI-flagged sentences in research papers to pass AI detectors without changing facts, citations, or meaning).
**Both models tested** at the product's real granularity: rewrite only the flagged sentences, reinsert into the paper, and score the reassembled text on ZeroGPT and Copyleaks.
**Date:** 2026-10-08.

---

## 1. At a glance

| | **humarin/chatgpt_paraphraser_on_T5_base** | **gemini-3.5-flash-lite** |
|---|---|---|
| Type | T5 seq2seq paraphraser (**not an LLM**) | Instruction-following **LLM** (multimodal, reasoning-capable) |
| Parameters | ~223M (open weights) | Not disclosed (proprietary) |
| Developer | humarin (community) | Google |
| How it's used | Fixed transform — feed a sentence, get a paraphrase; **no prompting** | **Prompted** — you instruct the behaviour and the constraints |
| Where it runs | Locally, CPU, **offline** | Google API (cloud) |
| Cost | **Free** (open model) | **Free tier** ($0, rate-limited); paid $0.30 in / $2.50 out per 1M tokens |
| Speed | ~0.45 sentences/sec on CPU | ~3 s per sentence via API |
| Data privacy | Fully local — nothing leaves the machine | Sent to Google; free tier may be used to improve products, paid tier not |
| Link | https://huggingface.co/humarin/chatgpt_paraphraser_on_T5_base | https://ai.google.dev/gemini-api/docs/models/gemini-3.5-flash-lite |

---

## 2. Test results

Both were tested with the same method — humanize the flagged sentence(s), reinsert into the mostly-human paragraph, and run the result through the detectors.

| Criterion | humarin | gemini-3.5-flash-lite |
|---|---|---|
| Evasion (sentence-level reinsertion) | ✅ Copyleaks 0% | ✅ ZeroGPT 0% · Copyleaks 0% |
| Evasion (whole text, on its own) | ❌ ZeroGPT 100% → 100% | Not the use case; prompts restyle effectively in context |
| Fact / number / citation preservation | Generally preserved, **but uncontrollable** | Preserved **and enforceable** (prompt rule + automated check) |
| Observed failure | Drifted a claim: "maximizing operational efficiency" → "driving down operational costs" | Fabricated a citation (prompt-example leak) — **found and fixed**; checker now blocks added citations |
| Control over output | None — fixed behaviour, cannot be instructed | Full — can be told "keep every citation, change no number" |
| Restyling ability | Synonym swaps only; keeps formal structure | True casual restyle (the thing that moves detector scores) |

**Key observation:** at the product's granularity, **both reach 0%** — so evasion alone does not separate them. The deciding factor is **fidelity control**.

---

## 3. Core difference

- **humarin** is a small, fixed paraphraser. It is fast, free, private, and faithful in the simple cases — but it **cannot be steered**. It only swaps synonyms (so on its own it does not evade detectors), and when it does change wording it occasionally **alters meaning** with no way to prevent it. For research papers, an unenforceable fidelity risk is a serious problem.

- **gemini-3.5-flash-lite** is an instruction-following LLM. It can be **commanded** to restyle aggressively *and* to leave every fact and citation untouched, and that constraint can be **verified automatically** (the harness flags any missing or added number/citation). It costs API calls and sends text to Google, but it is the only one of the two that gives **controllable, checkable fidelity** together with real restyling.

---

## 4. Recommendation

| Priority | Better choice |
|---|---|
| Fidelity control + reliable restyling (the project's hard requirement) | **gemini-3.5-flash-lite** |
| Zero cost, fully offline, maximum data privacy | **humarin** |

For a research-paper humanizer where **fact and citation preservation is non-negotiable**, **gemini-3.5-flash-lite is the better fit**: it both restyles (so it genuinely humanizes) and lets us enforce and verify the "do not touch the facts" rule. humarin remains useful where offline/free/private operation outweighs the lack of control, but it cannot guarantee faithfulness and cannot restyle on its own.

---

*Notes:* Gemini parameter count is not published by Google (all frontier commercial LLMs keep this closed). Detector tests were run on ZeroGPT and Copyleaks (Copyleaks at sensitivity 2/3); not yet validated on GPTZero.
