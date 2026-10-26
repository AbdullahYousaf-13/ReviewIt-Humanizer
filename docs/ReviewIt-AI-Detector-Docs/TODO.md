# To-Do

Branch: `abdullah/humanizer-new-engine` (ReviewIt, from `origin/main`)

## 1. Three results per humanize click (Gemini main, Humarin + T5 options)
- [ ] Run Gemini, Humarin, T5 on every `/api/humanize-sentence` call
- [ ] Pass each result through the candidate guard and score it
- [ ] Keep existing response keys unchanged
- [ ] Add `alternatives: [{engine, humanized, new_score}]` for the other two
- [ ] Gemini result = main (`humanized`, `engine`); omit engines that fail the guard
- [ ] Fallback when Gemini is unavailable: best of the other two becomes main
- [ ] Run the three engines in parallel; respect Gemini/humanize slot limits
- [ ] Update `service.py` response
- [ ] Update `API_FLOW.md` (new key)
- [ ] Add/adjust tests (fake Gemini)
- [ ] Tell the colleague about the new key (no edits under `ReviewIt/frontend`)

## 2. Enhance the Gemini prompt
- [ ] Review the current prompt against the research docs
- [ ] Draft improved prompt variants
- [ ] Compare variants on the 20-sentence set (fidelity + ZeroGPT/Copyleaks/GPTZero)
- [ ] Verify Gemini model name/options before using them
- [ ] Put the winning prompt into `_tier_gemini` and re-test

## 3. Branch
- [x] Create `abdullah/humanizer-new-engine` from main
