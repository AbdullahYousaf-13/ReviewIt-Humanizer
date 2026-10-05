# Models Research — ReviewIt Humanizer

## Local Paraphrase Models (Non-LLM) — Tested Locally

> Run via `test_humanizer_models.py` on CPU in the project `.venv`. These are small
> seq2seq paraphrasers that run offline (no API, no rate limits).

### `humarin/chatgpt_paraphraser_on_T5_base` — ❌ FAILS EVASION

| Spec | Value |
|---|---|
| Category | Seq2seq paraphraser (NOT an LLM) |
| Base | google-t5/t5-base |
| Size | 223M params |
| License | OpenRAIL |
| Training data | Quora + SQuAD 2.0 + CNN news paraphrase pairs |
| Speed (CPU) | ~0.45 sent/sec on short sentences; ~10s on a full paragraph |
| Facts/citations | ✅ Preserved perfectly (numbers 23.4%, 0.91 and citations intact) |
| **Evasion result** | ❌ **ZeroGPT 100% AI → 100% AI (no movement)** |

**Verdict:** Preserves meaning faithfully but does only conservative synonym swaps
("transformative"→"paradigm", "simulate"→"imitate"). Sentence structure, length, and
register are untouched — which is exactly what detectors key on. Failed on ZeroGPT, the
*easiest* of the three targets; will not do better on GPTZero/Copyleaks.

**Key insight:** This whole CLASS of model (humarin, bart-paraphrase, pegasus) is trained
on paraphrase-identification datasets to make minimal faithful edits. None were trained to
change STYLE, and style is what detection responds to. Faithful paraphrasing ≠ evasion.
What actually moves detector scores is aggressive restyling (fragmentation, simplification,
casual voice) — an instruction-following task (LLM), not paraphrasing.

### `eugenesiow/bart-paraphrase` — ❌ FAILS (too conservative + content loss)

| Spec | Value |
|---|---|
| Base | facebook/bart-large |
| Size | 406M params |
| License | Apache 2.0 |
| Speed (CPU) | ~0.07 sent/sec on a full paragraph (~14s) |
| Facts/citations | ⚠️ Dropped/merged a sentence when fed a whole paragraph (content loss) |
| Evasion result | Not detector-confirmed; output nearly identical to input — expected to fail |

**Verdict:** Even more conservative than humarin — minimal word changes, and it merged/dropped
content on long inputs. Same faithful-paraphrase limitation; no evasion value.

### `tuner007/pegasus_paraphrase` — ❌ FAILS (summarizer — drops content)

| Spec | Value |
|---|---|
| Base | PEGASUS (google/pegasus) |
| Size | 569M params |
| Speed (CPU) | ~0.12 sent/sec (~8.7s/sentence) |
| Facts/citations | ❌ Drops clauses (it's a summarization model) — removes information |
| Evasion result | Not viable: content loss disqualifies before detector testing |
| Note | `embed_positions` weights re-init under current transformers (quality risk) |

**Verdict:** PEGASUS is a summarizer at heart — it shortens and omits detail, which breaks the
"don't remove information" constraint. Worse fit than humarin/bart for this use case.

### Conclusion on faithful paraphrasers

humarin, bart-paraphrase, and pegasus all **fail evasion**. They either keep the formal
structure detectors key on (humarin, bart) or lose content (bart on long input, pegasus).
The next non-LLM avenue is **style-transfer / simplification** models that change register
and structure (e.g. Styleformer formal→casual) — not faithful paraphrasers.

---

## Models Tried in This Project

> All models used for humanization are **LLMs (Large Language Models)** — text-in, text-out models capable of following instructions and rewriting content. Not all models on the Groq account are LLMs (Whisper = speech-to-text, Orpheus = text-to-speech, Prompt Guard = safety classifier).

---

### 1. `qwen/qwen3.8-27b` — Groq ⭐ BEST SO FAR

| Spec | Value |
|---|---|
| **Category** | **LLM** |
| Provider | Groq |
| Developer | Alibaba (Qwen team) |
| Architecture | MoE (Mixture of Experts), 27B total params |
| Type | Hybrid — thinking + non-thinking (disable with `/no_think`) |
| Context Window | 32,768 tokens |
| Status | ✅ Working |
| **Free Tier — RPM** | 30 |
| **Free Tier — RPD** | 1K |
| **Free Tier — TPM** | 8K |
| **Free Tier — TPD** | 200K |
| **Free Tier — OTPM (measured)** | 1,000 (hidden limit, not in docs) |
| **Dev Tier — RPM** | 1,000 |
| **Dev Tier — RPD** | 500K |
| **Dev Tier — TPM** | 250K |
| Dev Tier — OTPM | Unknown — likely higher than free |
| Speed | Fast on Groq hardware |
| Detection Risk | Low — non-GPT architecture, less fingerprinted by detectors |
| Issues Found | 1,000 OTPM hidden limit forces 8s sleep between calls |
| Pricing | Check console.groq.com/pricing |

**Notes:**
- The 250K TPM is the documented combined limit
- Groq applies a separate hidden OTPM=1,000 per organization (confirmed by measurement)
- The OTPM is the real bottleneck, not TPM
- `/no_think` disables internal chain-of-thought to save tokens

---

### 2. `openai/gpt-oss-20b` — Groq

| Spec | Value |
|---|---|
| **Category** | **LLM** |
| Provider | Groq |
| Developer | OpenAI |
| Architecture | 20B parameter reasoning model |
| Type | Reasoning (thinks internally before responding) |
| Context Window | ~128K tokens |
| Status | ✅ Working |
| **Free Tier — RPM** | 30 |
| **Free Tier — RPD** | 1K |
| **Free Tier — TPM** | 8K |
| **Free Tier — TPD** | 200K |
| **Dev Tier — RPM** | 1,000 |
| **Dev Tier — RPD** | 500K |
| **Dev Tier — TPM** | 250K |
| Speed | Slow — burns thousands of tokens on internal thinking |
| Detection Risk | **Very High** — GPT-family, most fingerprinted by all detectors |
| Pricing | Check console.groq.com/pricing |

**Issues Found:**
- Hallucinations — added content not in original paper
- Token exhaustion — needed `max_tokens=4096+` just to get output
- Made paper go from 4% → 20% AI detection (worse than original)
- Slow per call due to reasoning overhead
- Required 30–45s retry waits on rate limits

---

### 3. `openai/gpt-oss-120b` — Groq

| Spec | Value |
|---|---|
| **Category** | **LLM** |
| Provider | Groq |
| Developer | OpenAI |
| Architecture | 120B parameter reasoning model |
| Type | Reasoning |
| Context Window | ~128K tokens |
| Status | ✅ Available (not yet tested) |
| **Free Tier — RPM** | 1,000 |
| **Free Tier — RPD** | 500K |
| **Free Tier — TPM** | 250K |
| Speed | Slower than 20b due to larger size |
| Detection Risk | **Very High** — larger GPT model, even more fingerprinted |

**Notes:**
- Not tested — likely has same or worse issues as gpt-oss-20b
- Larger size means more reasoning tokens = slower and more expensive

---

### 4. `llama-3.3-70b-versatile` — Groq

| Spec | Value |
|---|---|
| **Category** | **LLM** |
| Provider | Groq |
| Developer | Meta |
| Architecture | Dense transformer, 70B parameters |
| Type | Standard instruction-tuned |
| Context Window | 128K tokens |
| Status | ❌ 404 — Not available on this account |
| Speed | 276–400 t/s on Groq hardware |
| Detection Risk | Low — open source, underrepresented in detector training data |

**Notes:**
- Best overall model for this use case if accessible
- Not available on free/limited Groq accounts
- Would be first choice if account access is granted

---

### 5. `llama-3.1-8b-instant` — Groq

| Spec | Value |
|---|---|
| **Category** | **LLM** |
| Provider | Groq |
| Developer | Meta |
| Architecture | Dense transformer, 8B parameters |
| Type | Standard instruction-tuned |
| Context Window | 128K tokens |
| Status | ❌ 404 — Enterprise only |
| Speed | 750–900 t/s (fastest model on Groq) |
| Detection Risk | Low — open source |

**Notes:**
- Restricted to enterprise Groq accounts only
- Fastest model on Groq hardware but smaller quality than 70B

---

### 6. `llama3-8b-8192` — Groq

| Spec | Value |
|---|---|
| **Category** | **LLM** |
| Provider | Groq |
| Developer | Meta |
| Architecture | Dense transformer, 8B parameters |
| Type | Standard instruction-tuned |
| Context Window | 8,192 tokens |
| Status | ❌ Decommissioned by Groq |

**Notes:**
- Groq removed this model entirely
- Replaced by llama-3.1-8b-instant (enterprise) and llama-3.3-70b-versatile

---

## Overall Ranking

| Rank | Model | Status | Why |
|---|---|---|---|
| 1 | `qwen/qwen3.8-27b` | ✅ Working | Best accessible model — low detection risk, fast, good quality |
| 2 | `llama-3.3-70b-versatile` | ❌ Not accessible | Would be best choice — faster, larger, less detectable |
| 3 | `llama-3.1-8b-instant` | ❌ Enterprise only | Fast but enterprise-gated |
| 4 | `openai/gpt-oss-20b` | ✅ Working | Too detectable, hallucinations, slow |
| 5 | `openai/gpt-oss-120b` | ✅ Available | Not tested, likely worse than 20b for our use case |
| 6 | `llama3-8b-8192` | ❌ Dead | Decommissioned |

---

## Groq Full Model Availability (as of Oct 2025)

Models returned by `client.models.list()` on this account:

| Model ID | Category | Use |
|---|---|---|
| `allam-2-7b` | LLM | Arabic language model |
| `canopylabs/orpheus-arabic-saudi` | TTS (not LLM) | Text to speech — Arabic |
| `canopylabs/orpheus-v1-english` | TTS (not LLM) | Text to speech — English |
| `meta-llama/llama-prompt-guard-2-22m` | Classifier (not LLM) | Safety classifier |
| `meta-llama/llama-prompt-guard-2-86m` | Classifier (not LLM) | Safety classifier |
| `openai/gpt-oss-120b` | LLM | Chat — reasoning |
| `openai/gpt-oss-20b` | LLM | Chat — reasoning |
| `openai/gpt-oss-safeguard-20b` | Classifier (not LLM) | Safety model |
| `qwen/qwen3.8-27b` | LLM | Chat — hybrid thinking ✅ Using this |
| `whisper-large-v3` | STT (not LLM) | Speech to text |
| `whisper-large-v3-turbo` | STT (not LLM) | Speech to text |

---

## Groq Documented Rate Limits (Free Tier)

*Source: console.groq.com/docs/rate-limits — verified Oct 2025*
*Note: OTPM is a separate hidden per-org limit not shown in this table*

| Model | RPM | RPD | TPM |
|---|---|---|---|
| canopylabs/orpheus-arabic-saudi | 250 | 100K | 50K |
| canopylabs/orpheus-v1-english | 250 | 100K | 50K |
| meta-llama/llama-prompt-guard-2-22m | 100 | 50K | 30K |
| meta-llama/llama-prompt-guard-2-86m | 100 | 50K | 30K |
| openai/gpt-oss-120b | 1,000 | 500K | 250K |
| openai/gpt-oss-20b | 1,000 | 500K | 250K |
| openai/gpt-oss-safeguard-20b | 1,000 | 500K | 150K |
| **qwen/qwen3.8-27b** | **1,000** | **500K** | **250K** |
| whisper-large-v3 | 300 | 200K | — |
| whisper-large-v3-turbo | 400 | 200K | — |

**Developer Plan is significantly better than Free:**
- Free: 30 RPM / 8K TPM
- Developer: 1K RPM / 250K TPM (33x more requests, 31x more tokens)
- Currently unavailable due to high demand — join waitlist at console.groq.com/settings/billing

---

## Key Findings

- **Hidden OTPM limit:** Groq applies a 1,000 OTPM per-org limit not shown in docs — confirmed by measurement on `qwen/qwen3.8-27b`
- **GPT models are worst for detection evasion:** GPTZero achieves 99.3% accuracy on GPT-family output
- **Open source models (Llama, Qwen) are less detectable** because detectors were trained primarily on GPT/ChatGPT output
- **Reasoning models are a trap:** Both `openai/gpt-oss-20b` models burn tokens on internal thinking, need `max_tokens=4096+`, and are slow
- **Dev tier upgrade currently unavailable** on Groq due to high demand (as of Oct 2025)
