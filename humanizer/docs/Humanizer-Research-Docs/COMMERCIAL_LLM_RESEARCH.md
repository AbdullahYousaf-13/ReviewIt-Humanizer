# Commercial LLM Research (via Prompting) — ReviewIt Humanizer

> Commercial LLMs via API + prompting (Gemini Flash, DeepSeek, Perplexity, Groq/Qwen) for sentence-level humanization that evades detectors while preserving facts/citations.
> Earlier Groq LLMs → [LLM_RESEARCH.md](LLM_RESEARCH.md); non-LLM models → [MODEL_RESEARCH.md](MODEL_RESEARCH.md); evasion models → [EVASION_MODELS_RESEARCH.md](EVASION_MODELS_RESEARCH.md).
> Facts verified 2026-10-07 (Gemini docs 2026-10-06). Prices USD per 1M tokens.

## Headline
Naive prompting does **not** make a commercial LLM undetectable. The HumanGPT test (Oct 2026) ran GPT-5.5, Claude Sonnet 5, Gemini 3.1 Pro, DeepSeek V4 Pro through GPTZero → 176/176 flagged; a "sound human" prompt changed nothing (48/48 still 1.000), and GPTZero retrains on current model output. **The lever is the prompt + pipeline, not the model** — what works is aggressive restyle + sentence-level reinsertion (see Empirical results).

## Recommended models
| Model (API id) | Free tier | Paid in/out /1M | Notes |
|---|---|---|---|
| Gemini 3.5 Flash-Lite `gemini-3.5-flash-lite` | ✅ | $0.30 / $2.50 | **harness default** — fast, no reasoning tax |
| Gemini 3.8 Flash `gemini-3.8-flash` | ✅ | $0.75 / $3.75 | newest; reasoning-heavy (~48s/sentence; bills thinking tokens) |
| Gemini 3.6 Flash `gemini-3.6-flash` | ✅ | $0.75 / $3.75 | lighter than 3.8 |
| DeepSeek V4.1-Flash `deepseek-flash` | ~none | $0.14 / $0.28 | 1M ctx; OpenAI+Anthropic APIs; price rise announced |
| Qwen 3.8-27B (Groq) `qwen/qwen3.8-27b` | ✅ | Groq rates | baseline / control |
| Perplexity `sonar` | limited | $1/$1 + search fee | ⚠️ RAG — injects citations/content; expected to fail fidelity → rank last |

Deprioritized: GPT-family (most detectable — GPT-5.5 scored 1.000). Other live Gemini ids: `gemini-3.5-flash` ($1.50/$9), `gemini-3.1-flash-lite`, alias `gemini-flash-latest`; Gemini 2.5 Flash/Lite now access-limited to prior users.

## Billing (how to pay)
All **pay-as-you-go per token** (no flat monthly fee). Gemini/Groq = monthly invoice (card linked once); DeepSeek/Perplexity = prepaid credits. **Gemini free tier = $0** (no card, rate-limited by requests/day) — enough for testing. Free-tier Gemini may use prompts to improve products; paid tier doesn't.

## Prompts (API harness, default A)
Shared rules: simplest everyday words; short sentences (8–15 words), varied; no formal connectors (however, moreover, furthermore, thus, hence, consequently, thereby, nevertheless); **keep every number/citation exactly; NEVER add a citation/author/year not already present**; no new info; output only the rewrite.
- **A** plain restyle · **B** aggressive + fact-lock (voice of a tired grad student; 2–3 uneven short sentences; may start "And/But") · **C** persona + burstiness (mix fragments with one longer clause).

⚠️ Never put a concrete example citation in the prompt — the model copies it out as a fake reference.

## Empirical results (2026-10-08)
Real pipeline: humanize only the flagged sentence(s), reinsert, score on ZeroGPT + Copyleaks (sens. 2/3).

| Text | Before | After |
|---|---|---|
| Paragraph, 1 flagged sentence | — | ZeroGPT 0% · Copyleaks 0% |
| BERT abstract, 2 flagged sentences | Copyleaks 100% | **Copyleaks 0%** |
| 8 built-in sentences (all-AI block) | ZeroGPT 32% | ZeroGPT 0% |
| 10 sentences (all-AI block) | ZeroGPT 100% | ZeroGPT 38.7% (not passing) |

- Works on Copyleaks too; numeric facts preserved (they sit in untouched human sentences).
- Strongest on sparse flagged sentences in human text; an all-AI block only partially evades.
- Not yet tested on GPTZero.
- **Bug found & fixed:** model inserted a fake `(Smith et al., 2020)` — it copied the prompt's *example* citation. Fix: removed the example, added a "never add a citation" rule, and the fidelity checker now flags **added** (not just missing) numbers/citations. Lesson: no real-looking example facts in prompts.

## Sources
Gemini models/pricing/rate-limits (ai.google.dev, 2026-10-06) · DeepSeek (api-docs.deepseek.com) · Perplexity (docs.perplexity.ai) · GPTZero (gptzero.me) · HumanGPT test (humangpt.io/blog/which-ai-is-hardest-to-detect-2026).
