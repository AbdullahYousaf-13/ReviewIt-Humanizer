# Detection-Evasion Models Research — ReviewIt Humanizer

> DL models built specifically to evade AI-text detectors (2023–2026). Differ from general paraphrasers ([MODEL_RESEARCH.md](MODEL_RESEARCH.md)) and general LLMs ([LLM_RESEARCH.md](LLM_RESEARCH.md)). Targets: ZeroGPT, Copyleaks, GPTZero.

**Pattern (2026):** the effective evaders are small **non-LLM** models trained with multi-stage pipelines (SFT → preference optimization → refinement) that **release recipes, not weights** — you train your own. Those that release weights are LLMs with modest evasion. Turnitin 2025/26 retrained to catch humanizer output — it's a treadmill.

## MASH — Multi-stage Alignment for Style Humanization (ACL Findings 2026) ⭐ best fit
- **facebook/bart-base (140M)**, non-LLM; 4 stages: data build → style-injection SFT → DPO (detector confidence as reward) → inference refinement (GPT-4 polish, skippable).
- Reported **92% avg ASR** (6 datasets, 5 detectors); BERTScore ~0.9 (no explicit fact guarantee).
- Train: 1× RTX 3090, ~7.5h/domain. Inference ~3.1GB — CPU-feasible once trained.
- **Catches:** weights NOT released (must train, needs GPU); NOT tested on our 3 detectors (would need to DPO against them); Stage 4 uses GPT-4; no fact/citation preservation; research-only license; adversarial-trained detectors drop ASR to ~0.
- [Paper](https://arxiv.org/html/2601.08564) · [GitHub](https://github.com/githigher/MASH)

## Others
| Model | What | Fit |
|---|---|---|
| GradEscape (USENIX 2025) | 139M gradient-based evader; beats an 11B paraphraser | attack framework — needs victim-detector access to train |
| jialinyyzz/humanizer (2026) | Gemma 4–12B; SFT+DPO+GRPO; **weights released** | an LLM; modest (Originality 57%→85%); drops qualifiers ~1/3; untested vs our 3 |
| CoPA (EMNLP 2025) | training-free; off-the-shelf LLMs + contrastive guidance | LLM-based |

Also: AuthorMist, StealthRL → [LLM_RESEARCH.md](LLM_RESEARCH.md); DIPPER → [MODEL_RESEARCH.md](MODEL_RESEARCH.md).

## Takeaway
Best "build-your-own" path = **MASH** (small, cheap, CPU inference) but needs GPU training + DPO against our detectors + bolt-on fact preservation. **No ready-to-use non-LLM evader with released weights fits our constraints.**
