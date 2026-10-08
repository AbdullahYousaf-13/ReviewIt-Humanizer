# ReviewIt — Humanizer

Rewrites AI-flagged sentences in research papers so they read as human-written, **without
changing facts, citations, or meaning**. A separate upstream tool marks which sentences are
AI; this tool rewrites only those, and the rewrites are dropped back into the original text.
Target detectors: **ZeroGPT, Copyleaks, GPTZero**. Processing unit: a single sentence
(10–40 words).

## Approaches explored (no single "winner" chosen yet)

Three independent lines of work, all documented — see `docs/` for details:

1. **Commercial API LLMs via prompting** — `scripts/test_humanizer_api_llms.py`.
   Prompt-based restyling through Gemini / DeepSeek / Perplexity / Groq. Newest line of work;
   first results drop ZeroGPT/Copyleaks to 0% on realistic (sparse-flagged) text. See
   `docs/COMMERCIAL_LLM_RESEARCH.md`.
2. **Qwen via Groq pipeline** — `scripts/test_humanizer_llm.py`.
   Paragraph-level aggressive restyle (casual voice, fragmentation). See `docs/LLM_RESEARCH.md`.
3. **Local offline paraphrase models** — `scripts/test_humanizer_models.py`.
   Hugging Face seq2seq (humarin T5, BART, PEGASUS). Faithful but **failed evasion**. See
   `docs/MODEL_RESEARCH.md`.

## Project structure

```
scripts/
  test_humanizer_api_llms.py   # commercial API LLMs via prompting (Gemini/DeepSeek/Perplexity/Groq)
  test_humanizer_llm.py        # Qwen via Groq pipeline (paragraph-level)
  test_humanizer_models.py     # local Hugging Face paraphrase models (offline, no API)
data/
  <model>/<prompt>.txt         # run outputs: one combined file per prompt, numbered INPUT/OUTPUT sections
docs/
  BRIEF.md                     # project brief & findings
  COMMERCIAL_LLM_RESEARCH.md   # commercial API LLMs (Gemini/DeepSeek/Perplexity) + empirical results
  LLM_RESEARCH.md              # LLMs tried via Groq (Qwen, GPT-OSS, Llama)
  MODEL_RESEARCH.md            # non-LLM models (paraphrase / style / evasion)
  EVASION_MODELS_RESEARCH.md   # frontier detector-evasion models (MASH, GradEscape, etc.)
test_inputs.txt                # sample flagged sentences (one per line) for the API harness
requirements.txt
.env                           # API keys (not committed)
```

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

`requirements.txt` installs the API clients (`google-genai`, `openai`, `groq`, `python-dotenv`)
and PDF/DOCX parsing. The **local** paraphrase models additionally need `torch` + `transformers`
+ `sentencepiece`, and on Windows the Microsoft VC++ Redistributable (required by PyTorch).

**API keys** — put the ones you need in `.env` (none are committed):

```
GROQ_API_KEY=...
GEMINI_API_KEY=...        # free key: https://aistudio.google.com/apikey
DEEPSEEK_API_KEY=...
PERPLEXITY_API_KEY=...
```

## Usage

### Commercial API LLM harness (sentence-level, prompt-based)

Input is **one sentence per line** (or the built-in samples if no file is given). Output is one
combined file per prompt at `data/<model>/<prompt>.txt`, with numbered INPUT/OUTPUT sections.

```powershell
# Gemini (free tier) — defaults to gemini-3.5-flash-lite, prompt A, your own sentences:
.\.venv\Scripts\python.exe scripts\test_humanizer_api_llms.py test_inputs.txt

# a different provider (needs its key in .env): deepseek | perplexity | groq
.\.venv\Scripts\python.exe scripts\test_humanizer_api_llms.py deepseek test_inputs.txt

# run several prompt variants:
$env:LLM_PROMPTS="A,B,C"
.\.venv\Scripts\python.exe scripts\test_humanizer_api_llms.py test_inputs.txt
```

Knobs (env vars): `LLM_PROVIDER`, `LLM_MODEL` (Gemini default `gemini-3.5-flash-lite`),
`LLM_PROMPTS` (default `A`), `GEMINI_THINK` (`low`|`medium`|`high`). `gemini-3.8-flash` is
reasoning-heavy (~48s/sentence, can't go below `low`), so the default flash-lite is the fast/cheap
choice for bulk runs. The run prints a fidelity check per sentence that flags **missing
OR added** numbers/citations (added = hallucination).

### Qwen via Groq pipeline (paragraph-level)

```powershell
.\.venv\Scripts\python.exe scripts\test_humanizer_llm.py data\yourfile.pdf
```
Requires `GROQ_API_KEY`.

### Local paraphrase models (offline)

```powershell
.\.venv\Scripts\python.exe scripts\test_humanizer_models.py test_inputs.txt
.\.venv\Scripts\python.exe scripts\test_humanizer_models.py test_inputs.txt --model eugenesiow/bart-paraphrase
```
Input can be paragraphs — the script auto-splits into sentences (use `--no-split` to treat each
line as one unit).

## Findings so far

- **Commercial LLM prompting (Gemini Flash):** on the realistic pipeline (humanize only the
  flagged sentences, reinsert), a 100%-AI BERT abstract dropped to **0% on Copyleaks**, and the
  built-in set went **32% → 0% on ZeroGPT** — with numeric facts preserved. An *all-AI* block only
  reached 38.7%, so the approach is strongest on sparse flagged sentences in mostly-human text.
  A fabricated-citation bug (prompt's example citation leaking into output) was found and fixed.
  Details in `docs/COMMERCIAL_LLM_RESEARCH.md`.
- **Qwen via Groq:** aggressive restyle evades detectors at the paragraph level
  (`docs/LLM_RESEARCH.md`).
- **Local faithful paraphrasers — all FAIL evasion** (`docs/MODEL_RESEARCH.md`): `humarin T5` and
  `bart-paraphrase` keep formal structure (ZeroGPT 100% → 100%); `pegasus_paraphrase` drops
  content (breaks the fact constraint).

## How to test evasion (valid method)

1. Confirm the **original** AI text scores HIGH on a detector (e.g. ZeroGPT) first.
2. Run it through a script.
3. Paste the output back into the detector. A high→low drop = real evasion.

Testing text that already passes proves nothing. For the sentence-level tools, the most
meaningful score is on the **reassembled paragraph** (with the humanized sentences reinserted),
not a single sentence in isolation.
