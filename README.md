# ReviewIt — Humanizer

Rewrites AI-flagged sentences in research papers so they read as human-written, **without
changing facts, citations, or meaning**. A separate upstream tool marks which sentences are
AI; this tool rewrites only those. Target detectors: **ZeroGPT, Copyleaks, GPTZero**.

## Project structure

```
scripts/
  test_humanizer_llm.py      # LLM pipeline (Groq API) — current best approach
  test_humanizer_models.py   # local HF paraphrase models (offline, no API)
data/
  Input/                     # input text files (one sentence per line for the models script)
  outputs/                   # rewritten results
docs/
  BRIEF.md                   # project brief & findings
  MODELS.md                  # model research & test results
requirements.txt
.env                         # GROQ_API_KEY=... (not committed)
```

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Local paraphrase models also need `torch` + `transformers` + `sentencepiece`, and on Windows
the Microsoft VC++ Redistributable (required by PyTorch).

## Usage

**Local models (offline):**
```powershell
.\.venv\Scripts\python.exe scripts\test_humanizer_models.py data\Input\baseline_original.txt
.\.venv\Scripts\python.exe scripts\test_humanizer_models.py data\Input\baseline_original.txt --model eugenesiow/bart-paraphrase
```
Input = one sentence per line. Output is saved for pasting into the detectors.

**LLM pipeline (Groq):**
```powershell
.\.venv\Scripts\python.exe scripts\test_humanizer_llm.py data\Input\yourfile.pdf
```
Requires `GROQ_API_KEY` in the environment.

## Status

- **LLM (Qwen via Groq):** best result so far (aggressive restyle evades detectors).
- **Local paraphrasers (humarin T5, bart):** preserve facts perfectly but **fail evasion**
  (conservative synonym swaps — ZeroGPT 100% AI → 100% AI). See `docs/MODELS.md`.

## How to test evasion (valid method)

1. Confirm the **original** AI text scores HIGH on a detector (e.g. ZeroGPT) first.
2. Run it through a script.
3. Paste the output back into the detector. A high→low drop = real evasion.

Testing text that already passes proves nothing.
