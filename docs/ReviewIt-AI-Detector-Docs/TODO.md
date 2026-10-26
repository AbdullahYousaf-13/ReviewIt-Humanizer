# To-Do

Added 2026-10-26 from the supervisor's request. Work happens in the **ReviewIt** repo on branch `abdullah/humanize-new-engine` (created from `origin/main`).

## 1. Three responses per humanize click
Clicking a sentence now returns three rewrites instead of the single best one: **Gemini** (main, shown prominently), **Humarin** (option) and **T5** (option). The user may pick one of the two options instead of Gemini.

Decisions (2026-10-26, you): the API contract lock is lifted for this change only; the three-engine order replaces "Humarin → T5 → Gemini fallback"; running all three on every click (more Gemini calls and time) is accepted.

- [ ] Run Gemini, Humarin and T5 on every `/api/humanize-sentence` call (in `humanize_single_sentence_smart`, `backend/aidetector/pipeline/humanizer.py`), each through the existing candidate guard (citations, numbers, negation) and scored by the detector
- [ ] Keep the existing keys unchanged (`humanized`, `engine`, `new_score`, `improvement`, `failed`, `reason`); Gemini's result is the main one when it passes the guard, otherwise the best safe candidate as today
- [ ] Add one additive key, for example `alternatives: [{engine, humanized, new_score}]` for the other two (decide the exact shape; omit an engine whose rewrite failed the guard)
- [ ] Decide what happens when Gemini is unavailable (quota cooldown, no key, sentence with a citation rule): the best of the local two becomes the main one
- [ ] Run the engines in parallel to keep click latency down; respect `MAX_CONCURRENT_GEMINI` and the humanize slots
- [ ] Update `service.py` response, `API_FLOW.md` (new key, marked as added 2026-10-26) and tests (fake Gemini in `test_humanizer_decision.py`)
- [ ] Tell the colleague about the new key — frontend work (prominent Gemini, two options) is theirs; **do not edit `ReviewIt/frontend`**

## 2. Enhance the Gemini prompt as far as we can
Goal: the best possible results from Gemini (fidelity first, then lower detector score).

- [ ] Review the current prompt (QuillBot-style, "6th-8th grade", banned words, 2 examples) against the findings in `docs/Humanizer-Research-Docs` (`FINDINGS_20_set_test.md`, `COMMERCIAL_LLM_RESEARCH.md`)
- [ ] Draft improved prompt variants (fact/citation lock, stronger per-style guidance — see B9, burstiness/varied rhythm, no stock AI openers, keep register of the paper)
- [ ] Compare variants with the research harness (`scripts/test_humanizer_api_llms.py`, `LLM_PROMPTS`) on the 20-sentence set: fidelity check plus ZeroGPT / Copyleaks / GPTZero
- [ ] Verify the model name and the current Gemini API options before using them (no guessing)
- [ ] Put the winning prompt into the backend (`_tier_gemini`) and re-test

## 3. Branch
- [x] Create `abdullah/humanize-new-engine` from `origin/main` in ReviewIt and work on it from now on
