# LLM Research — ReviewIt Humanizer

> **Scope:** Large Language Models (decoder-only, instruction-following). Two groups:
> **(1)** general-purpose LLMs tried in the pipeline via the **Groq API**, and
> **(2)** dedicated detection-evasion LLMs (fine-tuned, self-hosted) researched but not used.
> For non-LLM paraphrase / style-transfer / simplification models, see
> [MODEL_RESEARCH.md](MODEL_RESEARCH.md).

All models here are **LLMs**. Not every model on the Groq account is an LLM (Whisper = STT,
Orpheus = TTS, Prompt Guard = safety classifier).

---

# Group 1 — General-purpose LLMs (Groq API)

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

## Overall Ranking (LLMs)

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

## Key Findings (LLMs)

- **Hidden OTPM limit:** Groq applies a 1,000 OTPM per-org limit not shown in docs — confirmed by measurement on `qwen/qwen3.8-27b`
- **GPT models are worst for detection evasion:** GPTZero achieves 99.3% accuracy on GPT-family output
- **Open source models (Llama, Qwen) are less detectable** because detectors were trained primarily on GPT/ChatGPT output
- **Reasoning models are a trap:** Both `openai/gpt-oss-20b` models burn tokens on internal thinking, need `max_tokens=4096+`, and are slow
- **Dev tier upgrade currently unavailable** on Groq due to high demand (as of Oct 2025)
- **LLM restyling is the only approach that has actually moved detector scores** in this
  project — faithful non-LLM paraphrasers do not (see [MODEL_RESEARCH.md](MODEL_RESEARCH.md))

---

# Group 2 — Dedicated detection-evasion LLMs (researched, not used)

> Specialized LLMs fine-tuned (via reinforcement learning) specifically to evade AI-text
> detectors. Same architecture family as Group 1 (Qwen, decoder-only), but task-specialized
> and **self-hosted** rather than API. Both **ruled out** for this project: they are LLMs
> (which we moved away from) and are impractical on a CPU-only machine.

### AuthorMist

| Spec | Value |
|---|---|
| Base | **Qwen2.5-3B-Instruct** (decoder-only LLM) |
| Training | RL (GRPO), one model per detector |
| Evasion | GPTZero 4%→92%, Sapling 2%→98%, Originality 0%→94% ASR; semantic sim >0.94 |
| Fit | ❌ LLM; **weights/code not released** (paper only); not tested on Copyleaks |
| Link | https://arxiv.org/html/2503.08716 |

### StealthRL — `suraj-ranganath/StealthRL`

| Spec | Value |
|---|---|
| Base | **Qwen3-4B-Instruct-2507** (decoder-only LLM) + LoRA (adapter-only release, MIT) |
| Trained vs | RoBERTa + Fast-DetectGPT; eval'd on RoBERTa/Fast-DetectGPT/Binoculars/MAGE |
| Evasion | Mean AUROC 0.79 → 0.43; TPR@1%FPR ≈ 0.024 |
| Fit | ❌ 4B LLM (CPU-impractical; needs GPU or paid `tinker` cloud). **Never tested vs ZeroGPT/Copyleaks/GPTZero** |
| Links | GitHub: https://github.com/suraj-ranganath/StealthRL · HF: https://huggingface.co/suraj-ranganath/StealthRL |
