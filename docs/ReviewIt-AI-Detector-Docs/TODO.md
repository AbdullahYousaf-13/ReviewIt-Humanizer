# To-Do

Branch: `abdullah/humanizer-new-engine` (ReviewIt, from `origin/main`)

## 1. Three results per humanize click (Gemini main, Humarin + T5 options)
- [x] Run Gemini, Humarin, T5 on every `/api/humanize-sentence` call
- [x] Pass each result through the candidate guard and score it
- [x] Keep existing response keys unchanged
- [x] Add `alternatives: [{engine, humanized, new_score}]` for the other two
- [x] Gemini result = main (`humanized`, `engine`); omit engines that fail the guard
- [x] Fallback when Gemini is unavailable: best of the other two becomes main
- [x] Run the three engines in parallel; respect Gemini/humanize slot limits
- [x] Update `service.py` response
- [x] Update `API_FLOW.md` (new key)
- [x] Add/adjust tests (fake Gemini)
- [x] Frontend: main result shown, other two as selectable options (colleague allowed FE edits for this change)

## 2. Enhance the Gemini prompt
- [x] Review the current prompt against the research docs (example citations in the prompt, sentence splitting, no settings)
- [x] Write one new prompt in `pipeline/gemini_prompt.py` (one call, 3 rewrites; no example facts/citations; keep each citation once; no added details; change structure; keep the paper's voice)
- [x] Remove the second-pass prompt/call (one prompt, one call)
- [x] Verify Gemini options against the installed SDK (google-genai 2.30.0): `system_instruction`, `temperature`, `thinking_config.thinking_level`
- [x] Set system instruction, temperature 1.0, thinking level low (env: `GEMINI_TEMPERATURE`, `GEMINI_THINK`)
- [x] Guard: reject a repeated or added citation
- [x] Tests for the prompt, the call settings and the guard
- [ ] Compare old vs new prompt on the 20-sentence set (fidelity + BERT score) — **waiting: the Gemini key is the free tier, no live calls for now**. Script: scratchpad `compare_prompts.py` (not committed)
- [ ] Manual ZeroGPT / Copyleaks check of the new prompt on reinserted paragraphs

## 3. Branch
- [x] Create `abdullah/humanizer-new-engine` from main
