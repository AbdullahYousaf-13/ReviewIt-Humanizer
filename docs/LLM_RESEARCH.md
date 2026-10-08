# LLM Research — ReviewIt Humanizer

> Decoder-only instruction LLMs: (1) general-purpose via the Groq API; (2) dedicated evasion LLMs (researched, not used). Non-LLM models → [MODEL_RESEARCH.md](MODEL_RESEARCH.md). Commercial API LLMs → [COMMERCIAL_LLM_RESEARCH.md](COMMERCIAL_LLM_RESEARCH.md).

## Group 1 — General-purpose (Groq API)

| Model | Status | Detection risk | Notes |
|---|---|---|---|
| `qwen/qwen3.8-27b` ⭐ | ✅ working (baseline) | Low (non-GPT) | 27B MoE, 32K ctx; `/no_think` saves tokens. Best accessible. |
| `openai/gpt-oss-20b` | ✅ working | Very high (GPT) | Reasoning model — hallucinations, slow, made detection worse (4%→20%). Avoid. |
| `openai/gpt-oss-120b` | available | Very high | Untested; likely worse than 20b. |
| `llama-3.3-70b-versatile` | ❌ 404 (not on account) | Low | Would be first choice if accessible. |
| `llama-3.1-8b-instant` | ❌ enterprise only | Low | Fastest on Groq. |
| `llama3-8b-8192` | ❌ decommissioned | — | Removed by Groq. |

**Groq free-tier limits (qwen):** 1,000 RPM / 500K RPD / 250K TPM documented, **but a hidden OTPM≈1,000 per-org** (measured) is the real bottleneck → ~8s between calls. Dev tier (much higher) is waitlisted.

### Key findings
- GPT-family worst for evasion (GPTZero ~99% on it); open models (Qwen/Llama) less fingerprinted.
- Reasoning models are a trap (burn tokens, slow).
- LLM restyling is the only approach that has moved detector scores; faithful non-LLM paraphrasers don't.

## Group 2 — Dedicated evasion LLMs (ruled out: LLMs + CPU-impractical)

| Model | Base | Evasion | Why ruled out |
|---|---|---|---|
| AuthorMist | Qwen2.5-3B, RL | GPTZero 4%→92%, Originality 0%→94% | weights/code not released; not tested vs Copyleaks |
| StealthRL | Qwen3-4B + LoRA (MIT) | mean AUROC 0.79→0.43 | 4B LLM, needs GPU; untested vs our 3 detectors |
