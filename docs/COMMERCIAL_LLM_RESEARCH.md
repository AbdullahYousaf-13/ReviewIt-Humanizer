# Commercial / General-Purpose LLM Research (via Prompting) — ReviewIt Humanizer

> **Scope:** General-purpose **commercial LLMs accessed by API and steered purely by
> prompting** (Gemini Flash family, Perplexity Sonar, DeepSeek, and the Groq/Qwen baseline),
> evaluated for sentence-level humanization that evades AI detectors **without changing facts,
> citations, or meaning**. This is the task the supervisor asked for: "which commercial LLMs
> work best at rewriting AI text to evade detectors while preserving facts/citations."
>
> For the earlier Groq-pipeline LLMs and self-hosted evasion LLMs, see
> [LLM_RESEARCH.md](LLM_RESEARCH.md). For non-LLM paraphrasers, see
> [MODEL_RESEARCH.md](MODEL_RESEARCH.md). For purpose-built evasion models, see
> [EVASION_MODELS_RESEARCH.md](EVASION_MODELS_RESEARCH.md). Target detectors:
> **ZeroGPT, Copyleaks, GPTZero.**

**All facts below verified on 2026-10-07** against official docs (Gemini models/pricing pages
last updated 2026-10-06; DeepSeek and Perplexity docs current). Prices are USD per 1M tokens.

---

## ⚠️ Headline finding (read before choosing a model)

**The premise "a commercial LLM, prompted to sound human, will pass detectors" is largely
contradicted by current (Oct 2026) public testing. Model choice is NOT the main lever — the
prompt and the pipeline are.**

- **HumanGPT, "Which AI Is Hardest to Detect? We Tested 4 in 2026"** ran **GPT-5.5, Claude
  Sonnet 5, Gemini 3.1 Pro, and DeepSeek V4 Pro** through GPTZero: **176/176 texts flagged**,
  175 at the maximum AI score of 1.000. Adding a "write like a real person" instruction changed
  nothing — **48/48 still flagged at 1.000**.
  (https://humangpt.io/blog/which-ai-is-hardest-to-detect-2026)
- **GPTZero** states it retrains on current model output (GPT-4.1/5/6, Gemini 2.5 Flash &
  Flash-Lite, Claude Sonnet 4, Llama, DeepSeek) and claims 99% accuracy. (https://gptzero.me/)

### Why this does NOT kill the project

1. **Those tests used weak, generic prompts** ("sound human"). This project's own BRIEF already
   found generic prompting does nothing — what moved scores was **aggressive restyling**
   (fragmentation, simplification, casual voice, banned connectors). The published failures
   never tested that.
2. **Processing unit is a single sentence (10–40 words).** Detectors are far noisier on short
   spans than on full essays, so doc-level reassembly is the number that matters.
3. **Model choice still matters for the other half of the task** — instruction-following
   fidelity and fact/citation preservation — even if not for raw evasion.

**Framing for the supervisor:** evaluate commercial LLMs as *"which model best executes an
aggressive restyle prompt while preserving facts,"* not *"which model is inherently
undetectable."* The latter is a dead end on current evidence.

---

## Recommended models (shortlist)

| Model (exact API ID) | Free tier | Paid in/out /1M | Speed | Evasion suitability | Fact/citation preservation |
|---|---|---|---|---|---|
| **Gemini 3.8 Flash** `gemini-3.8-flash` | ✅ yes | $0.75 / $3.75 | Fast* | Caught naively; strong at *following* restyle prompts | Strong |
| **Gemini 3.6 Flash** `gemini-3.6-flash` | ✅ yes | $0.75 / $3.75 | Fast | Same; lighter than 3.8 | Strong |
| **Gemini 3.5 Flash-Lite** `gemini-3.5-flash-lite` | ✅ yes | $0.30 / $2.50 | Fastest | Good for bulk passes | Good |
| **DeepSeek V4.1-Flash** `deepseek-flash` | ~none | $0.14 / $0.28 | Fast | Non-US model, still flagged naively | Strong |
| **Qwen 3.8-27B via Groq** (current baseline) | ✅ yes | Groq rates | Very fast | Current best; keep as control | Known working |
| **Perplexity Sonar** `sonar` / `sonar-pro` | limited | $1/$1 (+search fee) / $3/$15 | Medium | ⚠️ structural mismatch — see caveat | ⚠️ poor |

\* 3.8 Flash bills output **including thinking tokens** — it is reasoning-capable. Disable/minimize
the thinking budget for sentence rewriting or you pay the "reasoning tax" (slow, token-hungry)
this project already hit with `gpt-oss-20b`.

**Deliberately deprioritized:** GPT-family (`gpt-5.x`) — BRIEF already found it the most
detectable, and the HumanGPT test confirms GPT-5.5 scored 1.000. Use only as a negative control.

---

## Per-model detail

### Gemini 3.8 Flash — `gemini-3.8-flash` ⭐ quality-ceiling candidate

| Spec | Value |
|---|---|
| Developer | Google |
| Status | Newest **stable** Flash model (banner: "now available") |
| Positioning | "Long-horizon software engineering, autonomous agents, complex enterprise workflows" — reasoning-capable |
| **Free tier** | ✅ Free of charge, **no prior-use restriction**, no card required |
| Paid input | $0.75 /1M (→ $1.50 on 2027-01-01) |
| Paid output | $3.75 /1M **incl. thinking tokens** (→ $7.50 on 2027-01-01) |
| Context caching | $0.075 /1M |
| Alias | `gemini-flash-latest` points to latest Flash |
| Caveat | Set thinking budget to 0/minimal for sentence rewriting |

### Gemini 3.6 Flash — `gemini-3.6-flash` ⭐ balanced candidate

| Spec | Value |
|---|---|
| Status | Previous-gen stable Flash; lighter than 3.8 |
| Free tier | ✅ Free of charge, no restriction |
| Paid in/out | $0.75 / $3.75 (same as 3.8; → $1.50 / $7.50 in 2027) |

### Gemini 3.5 Flash-Lite — `gemini-3.5-flash-lite` ⭐ cheap/fast candidate

| Spec | Value |
|---|---|
| Status | Fastest, most budget-friendly stable Flash-Lite |
| Free tier | ✅ Free of charge |
| Paid in/out | $0.30 / $2.50 |
| Use | High-volume sentence passes where cost/latency dominate |

> Other live Gemini Flash IDs (verified in docs): `gemini-3.5-flash` (legacy, $1.50 / $9.00),
> `gemini-3.1-flash-lite`, `gemini-3-flash-preview`, `gemini-3.1-pro-preview`.
> Gemini **2.5** Flash/Flash-Lite are now access-limited to projects that used them before.

### DeepSeek V4.1-Flash — `deepseek-flash`

| Spec | Value |
|---|---|
| Model name | DeepSeek-V4.1-Flash (V4 family launched 2026-04-24) |
| Context | 1,048,576 tokens; max output 393,216 |
| API | OpenAI ChatCompletions **and** Anthropic Messages compatible |
| Input / output | $0.14 (cache miss) / $0.28 (cache hit input $0.0028) |
| Sibling | `deepseek-v4-pro` (DeepSeek-V4-Pro) $0.435 / $0.87 |
| Note | DeepSeek has announced a "significant" price increase is planned |
| Evasion | V4 Pro scored 1.000 on GPTZero in the HumanGPT test |

### Qwen 3.8-27B via Groq — current baseline (control)

Already in the pipeline (see [LLM_RESEARCH.md](LLM_RESEARCH.md)). Keep as the control so new
models are measured against the known-working setup. Groq free tier; hidden OTPM=1,000 limit
forces throttling.

### Perplexity Sonar — `sonar` / `sonar-pro` — ⚠️ low priority

| Model | Context | In / out | Extra |
|---|---|---|---|
| `sonar` | 127K | $1 / $1 | + per-request search fee $5–12 /1K |
| `sonar-pro` | 200K | $3 / $15 | + search fee $6–14 /1K |
| `sonar-reasoning-pro` | — | $2 / $8 | DeepSeek-R1 under the hood |

**Caveat (important):** Sonar is a **search-augmented (RAG)** system — every call retrieves live
web content and attaches **citations**. It is built to *answer questions with web info*, not to
faithfully rewrite a given sentence. For this project's hard constraints (no added facts, no
new/altered citations) this is a **structural mismatch** and is expected to fail fact
preservation. The supervisor named it, so run **one confirmatory test** with plain `sonar` and
`search_context_size: low`, but rank it last. (Perplexity Pro consumer subscription at $20/mo is
a separate product from the API.)

---

## How API billing works (how to pay)

**No LLM API here is a flat monthly subscription.** All are **pay-as-you-go — charged per token
actually used.** A month with zero calls costs $0. Two mechanics:

1. **Prepaid credits** — load a balance with a card; usage draws it down; top up (often
   auto-reload) when low. Used by **DeepSeek**, **Perplexity** (and OpenAI/Anthropic).
2. **Monthly invoice in arrears** — link a card once, use freely, pay month-end for actual
   usage. Used by **Google Gemini** (via a Google Cloud billing account) and **Groq** paid tier.

| Provider | Free tier | Paid model | Card to start? |
|---|---|---|---|
| Gemini | ✅ real free tier (key at aistudio.google.com/apikey) | Google Cloud monthly invoice | No card for free tier |
| Groq | ✅ free tier (already have) | Pay-as-you-go | — |
| DeepSeek | ~none | Prepaid balance | Yes |
| Perplexity | limited | Prepaid credits + auto-reload | Yes |

**For this project's test plan, cost = $0:** Gemini 3.8 Flash, 3.6 Flash, and 3.5 Flash-Lite all
run on the free tier (rate-limited — throttle between calls, same pattern as the Groq limits
already handled). Paid/prepaid setup is only needed to exceed free limits or to test
DeepSeek/Perplexity.

> **Privacy note:** On Gemini's **free tier**, Google may use prompts/outputs to improve its
> products; the **paid tier** does not. Fine for sample-paper testing; relevant if real
> client papers are ever sent. Exact top-up minimums / card requirements can change — confirm on
> each provider's console.

---

## Proposed test plan

**Principle:** hold the detector + test sentences constant; vary (a) model and (b) prompt
aggressiveness. Measure evasion **and** fidelity together — evasion is worthless if facts break.

1. **Fixed test set:** ~30–50 AI-flagged sentences (10–40 words) from real papers, each with its
   ground-truth numbers/citations recorded. Deliberately include citation-bearing and
   number-heavy sentences.
2. **Models (tier 1):** Gemini 3.8 Flash (thinking off), Gemini 3.6 Flash, Gemini 3.5 Flash-Lite,
   DeepSeek V4.1-Flash, Qwen-3.8-27B (control). **Tier 2 (optional):** Perplexity `sonar`.
3. **Prompts:** 3 variants per model (below) to separate "model effect" from "prompt effect."
4. **Evasion scoring:** run outputs through **ZeroGPT, GPTZero, Copyleaks** at two granularities —
   single sentence (noisy; report but don't over-trust) and **reassembled paragraph/document**
   (the number that matters).
5. **Fidelity scoring:** automated check that every number and citation survives verbatim **and
   that none are added** (catches hallucinated references), with number formats normalized
   (`27%`↔`27 percent`, `1,482`↔`1482`); optional embedding similarity / manual meaning check.
6. **Report:** per model × prompt — % AI (each detector, doc level), citation-loss rate,
   number-loss rate, latency, cost. **Winner = lowest doc-level AI score subject to zero
   citation/number loss.**

Implementation: **`scripts/test_humanizer_api_llms.py`** — multi-provider (Gemini / DeepSeek /
Perplexity / Groq), prompt-variant loop (A/B/C), and the fidelity checker above. Input = one
sentence per line (or built-in samples); output = one combined file per prompt at
`data/<model>/<prompt>.txt` with numbered INPUT/OUTPUT sections. Detector scoring stays manual
and separate (paste the OUTPUT paragraph into ZeroGPT/GPTZero/Copyleaks).

---

## Proposed prompts

**A — Baseline (current prompt).** Keep as-is for comparison (see [BRIEF.md](BRIEF.md)).

**B — Aggressive restyle + fact-lock:**

```
System: You are a plain-language copy editor. Rewrite the given sentence as a tired grad
student would explain it to a friend — casual, direct, uneven.

Rules:
- Swap every academic word for the simplest everyday one.
- Break it into 2–3 short sentences of uneven length (some 4–6 words, some 12–15) — vary the rhythm.
- You may start with "And" or "But."
- Never use: however, moreover, furthermore, thus, hence, consequently, thereby, nevertheless.
- Keep every number, statistic, and in-text citation EXACTLY as written — do not add, remove, or
  reword any citation or figure, and NEVER add a citation that was not already present.
- Add no new information. Output only the rewrite.
```

**C — Persona / burstiness:** same fact-lock clause, but instruct an explicit persona voice and
deliberate burstiness (mix fragments with one longer clause) to attack the low-variance signal
detectors key on.

> The **fact-lock clause is the critical addition** vs. the current prompt — it lets aggression
> rise (which is what moves detector scores) without breaking the hard constraints.
>
> ⚠️ **Do NOT put a concrete example citation in the prompt** (e.g. "Smith et al., 2020"). Models
> copy it into the output as a real reference — see the fabricated-citation bug below.

---

## Empirical results & lessons (2026-10-08)

First real runs of the harness (Gemini Flash via the casual-restyle prompt), humanizing **only the
flagged sentence(s)** and reinserting them into the source paragraph — the actual pipeline, not an
all-AI block. Detectors: **ZeroGPT** and **Copyleaks** (Copyleaks sensitivity 2/3).

| Text | Before | After (humanized + reinserted) |
|---|---|---|
| Paragraph with 1 flagged AI sentence | — | **ZeroGPT 0% · Copyleaks 0%** (both "human") |
| BERT abstract with 2 flagged AI sentences | **Copyleaks 100% AI** | **Copyleaks 0%** ("No AI Content Found") |
| 8 built-in sample sentences (all-AI block) | ZeroGPT 32% | **ZeroGPT 0%** |
| 10 test sentences (all-AI block) | ZeroGPT 100% | ZeroGPT **38.7%** (improved, not passing) |

**Takeaways:**
- **The real workflow works — on Copyleaks too, not just ZeroGPT.** Rewriting only the flagged
  sentences took a 100%-AI BERT abstract to 0% on Copyleaks, with every numeric result (GLUE 80.5%,
  SQuAD F1 93.2 / 83.1, etc.) preserved — they live in the untouched human sentences.
- **Strongest on sparse flagged sentences in mostly-human text** (the real case). An all-AI block
  only dropped to 38.7%: one humanized sentence among human text passes, but a wall of humanized
  sentences still carries residual AI signal.
- Not yet tested on **GPTZero**; small n; ZeroGPT/Copyleaks only.

### ⚠️ Bug found and fixed: fabricated citations

In 3/3 fact-free rewrites the model inserted **`(Smith et al., 2020)` — a citation that was never in
the original**. Root cause: `Smith et al., 2020` was the *example* citation written into the prompt
("e.g. Smith et al., 2020"); the model copied the example out as a real reference. In a research
paper this is a fabricated reference — academically fatal, and the detector score doesn't care
(a citation may even read as *more* human), so it passes silently.

**Fixes applied (`scripts/test_humanizer_api_llms.py`):**
1. Removed the concrete example from all prompts (A/B/C); added an explicit rule: *never add a
   citation, reference, author, or year not already in the sentence.*
2. Tightened the fidelity checker to flag **added** numbers/citations (hallucinations), not just
   missing ones, and to normalize number formats to avoid false flags. The old checker only caught
   dropped facts, so it was blind to this bug.

**Lesson for prompt design:** never put a realistic-looking fake citation or number in a prompt as
an example — models copy it into outputs.

---

## Sources (verified 2026-10-07; empirical tests 2026-10-08)

- Gemini models — https://ai.google.dev/gemini-api/docs/models (updated 2026-10-06)
- Gemini pricing — https://ai.google.dev/gemini-api/docs/pricing
- Gemini rate limits — https://ai.google.dev/gemini-api/docs/rate-limits
- DeepSeek models & pricing — https://api-docs.deepseek.com/quick_start/pricing/ ,
  https://api-docs.deepseek.com/api/list-models/ , change log https://api-docs.deepseek.com/updates/
- Perplexity pricing — https://docs.perplexity.ai/docs/getting-started/pricing
- GPTZero (detector retraining / accuracy claims) — https://gptzero.me/
- HumanGPT detectability test (Oct 2026) — https://humangpt.io/blog/which-ai-is-hardest-to-detect-2026
