# Findings — 20-Set Test: humarin vs. gemini-3.7-flash

**Question tested:** can each model humanize AI-written sentences inside real paper paragraphs so the paragraphs pass AI detectors again, without altering facts or citations?

Record files (full text of every set): [`data/humarin/record.md`](../data/humarin/record.md), [`data/gemini-3.7-flash/record.md`](../data/gemini-3.7-flash/record.md). Raw model outputs: `data/humarin/output.txt`, `data/gemini-3.7-flash/A.txt`.

---

## 1. Method

For each of 20 sets of 1–4 real paragraphs (from a published paper):

1. Paragraphs confirmed **human-written** on the detectors (a few AI-like sentences flagged in some).
2. One sentence per paragraph replaced with an **AI-generated sentence** (52 AI sentences in total; mix of fluff, number-bearing, and citation-bearing).
3. **Only those AI sentences** sent to the model for humanization (the harness's sentence-level mode).
4. Humanized sentences reinserted; the **whole paragraphs** re-tested on ZeroGPT and Copyleaks.

**Pass** = the detector reports no AI content for the set. **Fail** = it reports some AI content (ZeroGPT percentage recorded; Copyleaks results recorded as pass/fail only).

**Models and settings (harness defaults):** `humarin/chatgpt_paraphraser_on_T5_base` (T5, local, no prompt); `gemini-3.7-flash` (LLM, prompt A, thinking level low, temperature 1.0).

---

## 2. Results

| Set | gemini-3.7-flash ZeroGPT | gemini-3.7-flash Copyleaks | humarin ZeroGPT | humarin Copyleaks |
|---|---|---|---|---|
| 1 | Pass | Pass | Pass | **Fail** |
| 2 | Pass | Pass | **12%** | Pass |
| 3 | Pass | Pass | Pass | **Fail** |
| 4 | Pass | Pass | Pass | Pass |
| 5 | Pass | Pass | Pass | Pass |
| 6 | **14%** | Pass | **16%** | Pass |
| 7 | Pass | Pass | Pass | Pass |
| 8 | Pass | Pass | **34%** | Pass |
| 9 | Pass | Pass | Pass | **Fail** |
| 10 | Pass | Pass | Pass | Pass |
| 11 | Pass | Pass | Pass | Pass |
| 12 | **20%** | Pass | **32%** | **Fail** |
| 13 | **23%** | Pass | **57%** † | Pass |
| 14 | Pass | Pass | Pass | Pass |
| 15 | Pass | **Fail** | Pass | **Fail** |
| 16 | **32%** | Pass | **23%** | Pass |
| 17 | Pass | Pass | Pass | Pass |
| 18 | **23%** | **Fail** | **21%** | Pass |
| 19 | **11%** | **Fail** | **11%** | **Fail** |
| 20 | **4%** | Pass | Pass | Pass |

† **humarin Set 13 is unreliable:** its humanization run was generated from Set 12's sentences by mistake (re-run pending). Treated as invalid below.

### Summary

| | gemini-3.7-flash | humarin |
|---|---|---|
| **Passed both detectors** | **12 / 20 (60%)** | **8 / 20 (40%)** — 8 / 19 (42%) excluding Set 13 |
| Sets failing ZeroGPT | 7 | 8 (7 excluding Set 13) |
| Sets failing Copyleaks | 3 | 6 |
| Sets failing at least one | 8 | 12 |
| ZeroGPT AI% on failing sets (range / mean) | 4–32% / 18% | 11–34% / 21% (excluding Set 13) |

- **Passed by both:** Sets 4, 5, 7, 10, 11, 14, 17.
- **Failed by both:** Sets 6, 12, 13, 15, 16, 18, 19.
- **Passed by gemini only:** 1, 2, 3, 8, 9. **Passed by humarin only:** 20.

---

## 3. Findings

### 3.1 Evasion
- **gemini-3.7-flash evaded more often** (60% vs. 40–42% of sets) and failed Copyleaks half as often (3 vs. 6 sets).
- **ZeroGPT was the harder detector for both models.** The failing ZeroGPT scores are similar for the two (gemini 4–32%, humarin 11–34%), so the gap between models is mostly in *how many* sets fail, not how badly.
- **Neither model is reliable at this granularity.** A single humanization pass left 8 of 20 (gemini) and 12 of 20 (humarin) sets with detectable AI content.

### 3.2 Fidelity (checked programmatically against the raw outputs)

| | gemini-3.7-flash | humarin |
|---|---|---|
| Statistics preserved | **17 / 17** | **14 / 16** (Set 13 excluded) |
| Statistics lost | none | **Set 8:** "by up to **60%**" → "faster outbreak detection" (figure removed). **Set 17:** "an overwhelming **95%**" → "a vast majority" (figure removed). |
| Numbers/citations added | none | none |
| Citation instances duplicated | **Yes — Sets 3, 8, 13, 14, 18, 19** (a citation repeated after each split sentence, e.g. Set 13: 1 → 3) | none |

- **humarin silently deleted two statistics** while still passing the detectors on those sets (Set 8 fails ZeroGPT at 34%; Set 17 passes) — a hard-constraint violation the fidelity checker catches.
- **gemini kept every statistic** but tends to **split one sentence into several and repeat the citation after each**. The current checker compares *sets* of citations, so it does **not** flag this duplication; it needs a count-based check. In one case (Set 4) the citation also moved off the claim it supported.
- Meaning drift occurred in both: humarin reframed claims ("a major step forward" → "just the tip of the iceberg", Set 4; Set 17 recast educators' *concerns* as an asserted result); gemini added small details not in the source (e.g. "early" in Set 9; an extra sentence about false material spreading quickly in Set 18).

### 3.3 Patterns across sets
- **Strong set effect:** 7 sets failed for *both* models and 7 passed for both, so the text itself matters as much as the model.
- **Sets 1–11 vs. 12–20:** gemini passed 10/11 in the first group but only 2/9 in the second; humarin 5/11 vs. 3/9. The later sets come from the academic-integrity paper.
- **Possible confound (hypothesis, not proven):** in Sets 12, 13, 14 and 19 the replaced sentence was an *entire* single-sentence paragraph, so that paragraph consisted only of humanized text. Three of those four sets failed for both models (14 passed). Replacing a sentence inside a multi-sentence human paragraph may be easier to pass than replacing a whole paragraph.
- **Interpretation (hypothesis):** the humanized sentence is itself model-generated text, so detectors can still flag it when the rewrite stays formal or predictable.

---

## 4. Limitations

- Detector scores for the **with-AI paragraphs (before humanization)** were not recorded for all 20 sets, so the *improvement* attributable to each model cannot be quantified — only the end state.
- **humarin Set 13** is invalid (wrong input); one set is missing from humarin's comparison until re-run.
- Copyleaks results are pass/fail only; GPTZero was not run systematically.
- One run per model per set, no repeats — gemini output is non-deterministic (temperature 1.0), so individual set results can vary between runs.
- Sample is a single paper's topic area (healthcare AI and AI in education).

## 5. Relation to the earlier tests

The earlier demonstrations (4 hand-picked passages, `gemini-3.5-flash-lite` and humarin) reached 0% on the detectors. This systematic 20-set test shows pass rates of **60% (gemini-3.7-flash)** and **40% (humarin)**. The earlier results should be read as best-case demonstrations, not as the expected pass rate.

## 6. Open items
1. Re-run humarin Set 13 with the correct three sentences and update the record.
2. Record the with-AI (pre-humanization) detector scores to quantify the improvement.
3. Add a count-based citation check (duplicates) to the fidelity checker.
4. Test whether replacing a whole single-sentence paragraph is the cause of the Set 12/13/19 failures.
