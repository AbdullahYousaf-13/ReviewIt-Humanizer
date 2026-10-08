# Project Brief — Research Paper Humanizer

## What This Tool Does

Takes a research paper (PDF or DOCX), identifies AI-written sentences, and rewrites them so they pass AI detection tools — without changing any facts, citations, or meaning.

**Target detectors to evade:** ZeroGPT, Copyleaks, GPTZero

---

## Architecture

**Pipeline (the real use case):**
1. A separate upstream tool marks specific sentences as AI-written.
2. Our humanizer receives only those flagged sentences.
3. Each flagged sentence is rewritten individually.
4. Rewritten sentences replace the originals in the document.

**Processing unit:** single sentence (10–40 words typically).

> Why sentence-level matters: detectors score the *whole* passage. When only the few flagged
> sentences in a mostly-human paper are rewritten and reinserted, the residual AI signal is low —
> this is where evasion works best (see Findings).

---

## Approaches explored (no single approach chosen yet)

Three independent lines of work, all documented. None is declared the "final" approach.

| Approach | Script | Status / result | Doc |
|---|---|---|---|
| Commercial API LLMs via prompting (Gemini/DeepSeek/Perplexity/Groq) | `scripts/test_humanizer_api_llms.py` | Newest; drops ZeroGPT/Copyleaks to 0% on realistic text | `COMMERCIAL_LLM_RESEARCH.md` |
| Qwen via Groq pipeline (paragraph-level) | `scripts/test_humanizer_llm.py` | Aggressive restyle evades detectors | `LLM_RESEARCH.md` |
| Local offline paraphrase models (humarin/BART/PEGASUS) | `scripts/test_humanizer_models.py` | Faithful but FAILED evasion | `MODEL_RESEARCH.md` |

---

## What Has Been Tried

### Commercial API LLMs (via prompting) — `test_humanizer_api_llms.py`
- Providers: **Gemini** (`gemini-3.8-flash`, `gemini-3.5-flash-lite`), **DeepSeek** (`deepseek-flash`), **Perplexity** (`sonar`), **Groq** (`qwen/qwen3.8-27b`).
- Gemini Flash via a casual-restyle prompt is the main one tested so far. **`gemini-3.5-flash-lite` is the harness default** (fast/free, already clears ZeroGPT+Copyleaks); `gemini-3.8-flash` is reasoning-heavy (~48s/sentence even at minimum thinking) → too slow for bulk.
- Perplexity Sonar is search-augmented (RAG) → expected to inject citations/content; low priority.

### LLMs via Groq (paragraph-level) — `test_humanizer_llm.py`
| Model | Result |
|---|---|
| `qwen/qwen3.8-27b` | Working — aggressive restyle, low detection risk |
| `openai/gpt-oss-20b` | Hallucinations, slow, made detection worse (4% → 20%) |
| `llama-3.3-70b` / `llama-3.1-8b` | Not available on this account |

### Local paraphrase models — `test_humanizer_models.py`
- `humarin T5`, `bart-paraphrase`: conservative synonym swaps, keep formal structure → ZeroGPT 100% → 100% (failed).
- `pegasus_paraphrase`: summarizer, drops content → breaks the fact constraint.

### Key findings
- **GPT-family models are the worst for evasion** — most fingerprinted by detectors.
- **Faithful paraphrasing ≠ evasion.** What moves detector scores is changing **register and structure** (casual voice, fragmentation, simplification) — an instruction-following task, i.e. an LLM.
- **Reasoning models are a trap** for this task (slow, burn output tokens) — keep thinking off/minimal.

---

## Findings — commercial LLM prompting (2026-10-08)

Tested the real pipeline: humanize **only** the flagged sentence(s) and reinsert them. Detectors: ZeroGPT and Copyleaks (sensitivity 2/3).

| Text | Before | After (humanized + reinserted) |
|---|---|---|
| Paragraph with 1 flagged AI sentence | — | ZeroGPT 0% · Copyleaks 0% |
| BERT abstract with 2 flagged AI sentences | Copyleaks 100% AI | **Copyleaks 0%** |
| 8 built-in sample sentences (all-AI block) | ZeroGPT 32% | **ZeroGPT 0%** |
| 10 test sentences (all-AI block) | ZeroGPT 100% | ZeroGPT 38.7% (improved, not passing) |

- Works on **Copyleaks too**, not just ZeroGPT. Numeric facts (GLUE 80.5%, SQuAD F1, etc.) preserved because they sit in untouched human sentences.
- Strongest on **sparse flagged sentences in mostly-human text** (the real case); an all-AI block only partially evades.
- Not yet tested on **GPTZero**; small n.
- **Bug found & fixed:** the model inserted a fabricated `(Smith et al., 2020)` citation — it was copying the *example* citation written into the prompt. Fix: removed the example from all prompts + explicit "never add a citation" rule; the fidelity checker now also flags **added** numbers/citations. Lesson: never put a realistic fake citation/number in a prompt as an example.

---

## What Actually Works for Evasion

- Replace complex/academic words with simple everyday synonyms.
- Break long sentences into short ones (8–15 words); vary length (burstiness).
- Occasionally start sentences with "And" or "But".
- No formal academic connectors (however, furthermore, consequently, etc.).
- Write casually, not academically; sentence fragments are fine and help.

---

## Current Prompt Strategy (API harness)

Three prompt variants (A = plain restyle, B = aggressive restyle + fact-lock, C = persona/burstiness), default **A**. Core rules shared by all:

```
- Replace complex/academic words with the simplest everyday synonym.
- Break into short sentences (8–15 words); vary the rhythm.
- Do NOT use formal connectors: however, moreover, furthermore, thus, hence, consequently, thereby, nevertheless.
- Keep every number, statistic, and in-text citation EXACTLY as written.
- NEVER add a citation, reference, author, or year that is not already in the sentence.  ← critical
- Add no new information. Output only the rewrite.
```

> Do NOT include a concrete example citation (e.g. "Smith et al., 2020") in the prompt — models copy it into the output as a real reference.

---

## Hard Constraints

- Do NOT hallucinate — every fact, number, statistic must come from the original.
- Do NOT add, remove, or alter citations (e.g. Smith et al., 2020). **Adding a citation is as bad as dropping one** — it fabricates a reference.
- Do NOT add new content not in the original.
- Preserve all technical terminology (medical/scientific terms stay as-is).

---

## Tech Stack

- Language: Python
- PDF parsing: `pdfplumber`; DOCX: `python-docx`
- API clients: `google-genai` (Gemini), `openai` (DeepSeek/Perplexity/Groq-compatible), `groq`
- Local models: `transformers` + `torch` + `sentencepiece`
- Config: `python-dotenv` (keys in `.env`)

### Output layout (API harness)
`data/<model>/<prompt>.txt` — one combined file per prompt; each run appends a numbered section with its INPUT and OUTPUT paragraphs.

---

## Known Issues

- **Fabricated citations** (FIXED): prompt example citation leaked into output — see Findings.
- **All-AI blocks only partially evade** (38.7%); the approach relies on flagged sentences being sparse within human text.
- **`gemini-3.8-flash` is slow** (~48s/sentence) due to mandatory reasoning — prefer `gemini-3.5-flash-lite`.
- **Number-format drift** (e.g. "27%" → "27 percent") — the fidelity checker normalizes formats so this isn't falsely flagged.
- Groq free tier has a hidden OTPM≈1,000 limit → forces throttling between calls.
- Gemini free-tier rate limits are per-account (requests/day) and are the real bottleneck for bulk runs.

---

## What Is NOT Decided Yet

- Which approach/model to adopt as the production humanizer (commercial LLM vs Groq/Qwen vs other) — currently documenting all, no winner chosen.
- How sentences are marked/flagged and passed in by the upstream tool, and in what format.
- Evasion not yet validated on **GPTZero**, and only at Copyleaks sensitivity 2/3.
