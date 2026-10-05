# Project Brief — Research Paper Humanizer

## What This Tool Does

Takes a research paper (PDF or DOCX), identifies AI-written sentences, and rewrites them so they pass AI detection tools — without changing any facts, citations, or meaning.

**Target detectors to evade:** ZeroGPT, Copyleaks, GPTZero

---

## Current Architecture

1. User provides a PDF or DOCX file
2. Tool extracts text and splits into paragraphs
3. Each paragraph is sent to an LLM for rewriting
4. Output is saved as a `.txt` file

**Current model in use:** `qwen/qwen3.8-27b` via Groq API

---

## Planned Architecture (next phase)

1. A separate tool marks specific sentences as AI-written
2. Our humanizer receives only those flagged sentences
3. Each sentence is rewritten individually
4. Rewritten sentences replace the originals in the document

**Processing unit:** Single sentence (10–40 words typically)

---

## What Has Been Tried

### Models tried (all via Groq API — all LLMs):

| Model | Result |
|---|---|
| `openai/gpt-oss-20b` | Hallucinations, slow, made detection worse (4% → 20%) |
| `qwen/qwen3.8-27b` | Best so far — working, low detection risk |
| `llama-3.3-70b-versatile` | 404 — not on this account |
| `llama-3.1-8b-instant` | 404 — enterprise only |
| `llama3-8b-8192` | Decommissioned |

### Key findings:
- GPT-family models are the WORST for detection evasion — GPTZero achieves 99.3% accuracy on them
- Open-source models (Llama, Qwen) are less detectable
- Reasoning models (gpt-oss-20b) burn thousands of tokens on internal thinking — avoid
- ZeroGPT's own free humanizer tool achieved 0% on Copyleaks by using: aggressive word simplification, sentence fragmentation, breaking long sentences into short ones, and casual vocabulary

---

## What Actually Works for Evasion

Based on testing ZeroGPT's humanizer output against the original:

- Replace complex/academic words with simple everyday synonyms
- Break long sentences into short ones (8–15 words)
- Occasionally start sentences with "And" or "But"
- No formal academic connectors (however, furthermore, consequently, etc.)
- Write casually, not academically
- Sentence fragments are fine and help

---

## Current Prompt Strategy

```
System: "You are a plain-language editor. Rewrite academic text into simple, everyday English that a non-expert would write."

Rules:
- Replace every complex or academic word with its simplest everyday synonym
- Break long sentences into shorter ones — aim for 8 to 15 words per sentence
- Occasionally start a sentence with "And" or "But" to sound natural
- Do NOT use formal connectors: no however, nevertheless, consequently, moreover, furthermore, thus, hence, thereby
- Keep all facts and do not add or remove any information
- Preserve all in-text citations exactly as they appear
- Target length: ~{word_count} words — do not cut content to meet this
- Write like a person explaining something casually, not presenting research
```

---

## Hard Constraints

- Do NOT hallucinate — every fact, number, statistic must come from the original
- Do NOT remove or alter citations (e.g. Smith et al., 2020)
- Do NOT add new content not in the original
- Preserve all technical terminology (medical/scientific terms stay as-is)

---

## Current Tech Stack

- Language: Python
- PDF parsing: `pdfplumber`
- DOCX parsing: `python-docx`
- LLM API: Groq (`groq` SDK)
- Model: `qwen/qwen3.8-27b`

---

## Known Issues

- Groq free tier has hidden OTPM=1,000 limit (not in docs) — forces 8s sleep between calls
- Paragraphs sometimes come out 30–50% shorter than original (content loss)
- `Furthermore` occasionally appears in output despite being banned
- Rate limit retry parser reads actual Groq wait time from error message

---

## What Is NOT Decided Yet

- How sentences will be marked/flagged by the other tool
- What format flagged sentences will be passed in
- Whether to continue with LLMs or switch to pre-trained paraphrase models
