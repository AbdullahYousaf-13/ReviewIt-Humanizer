# ReviewIt — Humanizer

Rewrites AI-flagged sentences in research papers so they read as human-written, **without
changing facts, citations, or meaning**. An upstream tool marks which sentences are AI; this tool
rewrites only those and reinserts them. Targets: **ZeroGPT, Copyleaks, GPTZero**. Unit: one
sentence (10–40 words). See [docs/BRIEF.md](docs/BRIEF.md) for the current state and findings.

## Approaches (no winner chosen)

1. **Commercial API LLMs via prompting** — `scripts/test_humanizer_api_llms.py` (Gemini/DeepSeek/Perplexity/Groq). Newest; clears ZeroGPT+Copyleaks on realistic text. [docs/COMMERCIAL_LLM_RESEARCH.md](docs/COMMERCIAL_LLM_RESEARCH.md)
2. **Qwen via Groq (paragraph-level)** — `scripts/test_humanizer_llm.py`. [docs/LLM_RESEARCH.md](docs/LLM_RESEARCH.md)
3. **Local offline paraphrasers** — `scripts/test_humanizer_models.py` (humarin/BART/PEGASUS). Evade in context but fidelity isn't controllable. [docs/MODEL_RESEARCH.md](docs/MODEL_RESEARCH.md)

**Key finding:** at sentence-level reinsertion, evasion is easy (all methods hit ~0%) — **fidelity** is the real differentiator, and only LLM prompting lets you enforce "keep facts/citations."

## Structure

```
scripts/
  test_humanizer_api_llms.py   # commercial API LLMs via prompting
  test_humanizer_llm.py        # Qwen via Groq (paragraph-level)
  test_humanizer_models.py     # local HF paraphrasers (offline)
data/<model>/                  # run outputs (numbered INPUT/OUTPUT sections, one sentence per line)
docs/                          # BRIEF, COMMERCIAL_LLM_RESEARCH, LLM_RESEARCH, MODEL_RESEARCH, EVASION_MODELS_RESEARCH
test_inputs.txt                # sample flagged sentences (one per line)
.env                           # API keys (not committed)
```

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```
Installs API clients + `torch`/`transformers`/`sentencepiece` for local models (Windows: PyTorch needs the MS VC++ Redistributable).

API keys in `.env` (none committed): `GROQ_API_KEY`, `GEMINI_API_KEY` (free: https://aistudio.google.com/apikey), `DEEPSEEK_API_KEY`, `PERPLEXITY_API_KEY`.

## Usage

**Commercial API LLM harness** — one sentence per line; output → `data/<model>/<prompt>.txt`.
```powershell
# Gemini (free, default gemini-3.5-flash-lite, prompt A):
.\.venv\Scripts\python.exe scripts\test_humanizer_api_llms.py test_inputs.txt
# other provider: deepseek | perplexity | groq
.\.venv\Scripts\python.exe scripts\test_humanizer_api_llms.py deepseek test_inputs.txt
```
Env knobs: `LLM_MODEL`, `LLM_PROMPTS` (default `A`; e.g. `A,B,C`), `GEMINI_THINK`. The run prints a fidelity check flagging **missing OR added** numbers/citations.

**Local paraphrasers (offline)** — one sentence per line; output → `data/<model>/output.txt`.
```powershell
.\.venv\Scripts\python.exe scripts\test_humanizer_models.py bart test_inputs.txt
.\.venv\Scripts\python.exe scripts\test_humanizer_models.py Nubletz/bart-text-simplification test_inputs.txt
```
Models: `bart` (default), `pegasus`, `humarin`, or any HF seq2seq id.

**Qwen via Groq (paragraph-level):** `test_humanizer_llm.py data\yourfile.pdf` (needs `GROQ_API_KEY`).

## How to test evasion (valid method)
1. Confirm the **original** AI text scores HIGH on a detector first.
2. Humanize and reinsert.
3. Paste back into the detector — a high→low drop = real evasion.

Testing text that already passes proves nothing. Score the **reassembled paragraph**, not a lone sentence.
