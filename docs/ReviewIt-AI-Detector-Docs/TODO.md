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

## 2b. Supervisor fixes (2026-10-26)
- [x] Log the time of every run (total + per engine)
- [x] No model names on the page: "Recommended", "Option 2", "Option 3" (rule-based, when it wins, is also "Recommended")
- [x] Original sentence on top in the rewrite box, struck through with a spiky line, removed words in red; new words in green in each rewrite
- [x] Humarin, T5 and rule-based run only for the default style (academic); other styles: Gemini only, sentence kept with a neutral reason if Gemini gives nothing
- [x] Guard: "raises concerns/questions/issues" no longer counts as an upward word (it rejected good rewrites as "claim reversed")
- [x] A failed run is no longer shown as "Humanized" in the page (the sentence can be tried again)

## 2c. Fixes from the 2026-10-27 pipeline test
- [x] Prompt: add nothing from the surrounding sentences (no linking words or claims that point to them)
- [x] Prompt: keep every qualifier at the same strength (hedges, amounts, example markers, limits)
- [x] Prompt: restructure lists and definitions harder; 5 rewrites per call instead of 3 (all calls, same single call)
- [x] Prompt: full description for each of the 6 styles (register, sentence length, vocabulary, voice)
- [x] Gemini reply that stopped early (token limit, safety) is discarded
- [x] Guard: reject a rewrite that does not end like a sentence
- [x] PDF reader: skip back-matter sections (conflict of interest, funding, acknowledgements, data availability, ...)
- [x] Log tokens and cost of every Gemini call
- [x] Re-test the latest prompt: 36 calls, $0.0524 — see `GEMINI_PROMPT_V3_TEST_2026-10-27.md`

## 2d. Prompt/guard fixes from the final-prompt check, and old .doc files
- [x] Academic style: plain, common words (the formal word setting made rewrites score higher)
- [x] Narrative style: join the parts of the target sentence only; no new clause
- [x] Guard: reject a rewrite that adds a stock phrase (consequently, furthermore, thus, ...)
- [x] Guard: a prefix negation (unfamiliar, non-users) can stand in for "not"
- [x] Old .doc (Word 97-2003): not supported (supervisor decision 2026-10-27); refused with a clear message; LibreOffice uninstalled from this PC

## 2e. Supervisor updates (2026-10-27)
- [x] Show Gemini's two best rewrites: the best is the main result, the second is the first option (`alternatives`, engine "gemini"); no frontend change needed, the page already lists the options
- [x] Stronger Gemini prompt, research-based: verbs over nouns made from verbs; machine-text style words and patterns banned (guard enforces the words); varied rhythm; self-check of every rewrite before answering

## 2f. Issues in the current prompt (found in the 2026-10-27 test, to fix on 2026-10-28)
The latest prompt doubled evasion (Academic below 40%: 10 → 22 of 26) but its bolder rewrites changed meaning more seriously. See `GEMINI_PROMPT_V3_TEST_2026-10-27.md`.
- [ ] "We" added where the original has no first person (#21 twice, #23, #26): guard should reject an added "we / our / us / I"
- [ ] A comparison turned into a cause (#118: "using ChatGPT **made** students more willing"): meaning rule "never turn a comparison or a link into a cause"
- [ ] The relation between ideas distorted (#75): same rule, plus "keep how the parts relate"
- [ ] Who does what changed (Business #20: "Instructors will examine …"): meaning rule "keep who does what"
- [ ] A new subject added (#25: "Educators must …") and "Such" pointing to the context (#72 option 2)
- [ ] Creative adds a claim (#22: "Doubts multiply fast."): Creative may add a short sentence only to restate part of the target
- [ ] "Ethical and social" qualifiers dropped (#75, both rewrites)
- [ ] "The need" strengthened to "must" (#21)
- [ ] Two list sentences still score 100% in all 5 rewrites (#30, #32)
- [ ] **To check (reported 2026-10-27, paper `paperwithError_01`):** "Hao et al. examined the effect of restrictions …" — a citation written as "Name et al." with **no year** is not recognised as a citation. The check only knows `[12]` and `(…, 2023)`/`Name (2023)`, so this sentence is treated as uncited: it goes to Humarin and T5 too, and the guard does not check that "Hao et al." is kept.

## Backend (2026-10-27, before the demo)
- [x] One Gemini retry when none of the first five rewrites passes (asks for bolder changes; a failed call is not retried; at most two calls per click)
- [ ] **After the demo, discuss with the supervisor:** faster upload scoring — sort blocks by length before batching (measured 20.4 s → 13.8 s on the 7-page paper, identical scores) and use all 8 CPU cores (→ 12.7 s)

## FE (frontend changes — by default the colleague's; done here only when asked)
- [x] When a humanize attempt fails (no rewrite kept, `failed: true`), no popup; the sentence stays as it is. "Humanize all" counts only real rewrites and shows nothing if none was rewritten (`d917b5e`)
- [x] `.doc` removed from the upload file picker and drag-and-drop check (`components/dashboard/file-upload-card.tsx`)
- [x] Labels: Gemini's rewrites are "Recommended 1" and "Recommended 2"; Humarin and T5 are "Option 1" and "Option 2" (`components/dashboard/rewrite-box.tsx`)
- [ ] The landing page still says "PDF, DOCX, DOC, and TXT" (`components/landing/faq-section.tsx`, `features-section.tsx`): not changed

## Questions for the supervisor (after the demo)
- [ ] When Humarin or T5 scores much better than Gemini (example: Gemini 98% and 100% AI risk, Humarin 2%, T5 1%), which should be the main result? Today Gemini's best rewrite is always "Recommended 1" when it passes the guard and scores below the original, even if a local engine scores far lower. Options: keep Gemini first always; or put a local rewrite first when it scores lower by a clear margin (Gemini still shown).
- [ ] Faster upload scoring (see "Backend" above): sort blocks by length and use all CPU cores, same scores, about 38% faster.

## 2g. Supervisor changes (2026-10-28)
- [x] Par score 30% instead of 40% (backend `PAR_SCORE` in `config/settings.py`; frontend `lib/par.ts` used for colours, counts and labels)
- [x] Gemini asked for only 2 rewrites per call; best always shown if it beats the original, second only at 30% or below; one retry when none reaches 30%, results of both calls pooled
- [x] Humarin and T5 shown only at 30% or below
- [x] A Humarin / T5 rewrite at 30% or below goes first when none of Gemini's does; Gemini's best below it
- [x] Labels by rank: "Recommended", "Option 1", "Option 2", "Option 3" (`rewrite-box.tsx`)
- [x] Tags "Advanced" (Gemini) / "Standard" (others) added next to each label
- [ ] **BEFORE MERGING TO main — get the supervisor's approval:** each result now has a small neutral tag, "Advanced" (Gemini) or "Standard" (Humarin, T5, rule-based), next to its "Recommended" / "Option n" label (`components/dashboard/rewrite-box.tsx`, function `groupTag`, commit after `26378a5`). If not approved, delete `groupTag` and the `<span>` that shows it.
- [ ] Ask the supervisor: Gemini first whenever it has a result at 30% or below, even if Humarin / T5 score lower (today's rule)? And: Gemini asked for 2 rewrites instead of 5 may lower evasion (not measured)

## 3. Branch
- [x] Create `abdullah/humanizer-new-engine` from main
