# Project walkthrough — branch `abdullah/humanizer-dev`

Last updated 2026-10-26. This note covers the work on this branch. The original project (the detector, the first humanizer and the Flask API) was already there and is described only as the starting point. The frontend is now a separate piece of work by a colleague (see section 5).

---

## 1. The project in one minute

**What the app does.** You paste text or upload a document. The app reads it as paragraphs and headings, finds the sentences that look AI-written and marks them. You click a sentence and the app rewrites it so a detector scores it lower, without changing its facts. You can revert the rewrite or compare the original and the rewrite side by side.

**If someone asks "what did you do?"**

> The backend already had a detector and a humanizer. I made **Humarin the first rewriter** (Humarin → T5 → Gemini → rule-based) and made the API tell the page which rewriter won. I measured why rewriting was slow (mostly the Gemini free-tier key). I then made the backend **safe and structured**: uploads are read by layout as paragraphs and headings with the title page, references, tables and footnotes removed; every rewrite goes through a **guard** that rejects lost citations, changed numbers, reversed meaning and broken punctuation, and a failed rewrite is never inserted; sentences with citations go to Gemini only; a non-default style tries Gemini first; uploads and jobs are cleaned up, the models are preloaded, and requests are limited. I checked the reader on 9 real papers and wrote 217 tests. I also built a first test frontend; the colleague's new frontend replaced it, and the API shapes are now locked for it. Rewriting a whole document in one request is left out until I talk to my supervisor.

---

## 2. What changed on this branch

**Before:** Gemini was tried first. If it failed, T5 and then a rule-based rewriter were used. A local detector (BERT) scored every rewrite and the lowest score won, even when that rewrite was wrong. Uploads were read as one flat string.

**Now:** Humarin first (default style) with T5, Gemini and rule-based as fallbacks; a guard on every rewrite; a layout-aware document reader; the API tells the page the winner (`engine`), the paragraph of each sentence (`para`), the headings, notes about skipped pages, and whether a rewrite failed (`failed`, `reason`).

| Date | Commits | What |
|---|---|---|
| 13–14 Oct | `0d9384f`, `3d55e2a` | Humarin module and test scripts; Humarin added to the main pipeline; fallback order changed; `engine` added to the response |
| 14–16 Oct | `d17689a` … `7573adb` | First test frontend, backend fixes (one Gemini model, T5 candidates, hyphen, no invented scores, requirements), READMEs, issue lists |
| 19–20 Oct | `b197710` … `2d1a299` | Diverse-beam experiment (kept on an archive tag, not on this branch); T5 uses 3 beams |
| 20 Oct | `fc70ada`, `1c7a61d`, `387cef7`, `1147eed`, `f4b6696` | Paragraph and heading reader, the guard, upload clean-up, model preload, request limit, strict styles, skip Gemini on a used-up quota |
| 21 Oct | `96d6f3f`, `fde1cd8`, `81d5b42`, `8c9fa56`, `f9fd756` | Lowest safe score wins (no 0.15 margin), layout fixes found on real papers, soft errors for scanned files, citations → Gemini only, guard fixes, footnote and bullet fixes |
| 22 Oct | `6c6249a` … `2ab077a`, `baf13ba` | Root docs and the old frontend taken out of git; new frontend merged from `main`; non-default styles try Gemini first |

---

## 3. AI / ML side

### 3.1 How one rewrite is chosen
1. The detector scores the original sentence alone (0 = human, 1 = AI). This is the score to beat.
2. The routing picks the order of the rewriters:
   - **Sentence with a citation:** Gemini only.
   - **No citation, style `academic`:** Humarin → T5 → Gemini → rule-based.
   - **No citation, another style:** Gemini → Humarin → T5 → rule-based.
   The first one always runs; the next one runs only if nothing has helped yet or the best score is still 0.40 or more. Rule-based is the last resort (nothing helped, or best 0.50 or more).
3. Humarin writes 5 versions, T5 up to 3, Gemini 3 (and 3 simpler ones if the best is still 0.35 or more).
4. Every version passes the **guard** first. A rejected version is never scored or kept.
5. The versions that pass are scored by the detector. The **lowest score wins** if it is lower than the original's.
6. If none is safe and lower, the original is returned with `failed: true` and a reason.

The numbers to remember: **0.75** = the detector calls a sentence AI. **0.40** = our "good enough" line (green/amber, and when the next rewriter is tried). **0.50** = when the rule-based rewriter is used. **0.35** = when Gemini gets a second try.

### 3.2 Decisions

**Humarin is the first rewriter** *(you and your supervisor)*
- *Why:* it runs on your own computer. No key, no quota, no cost, no internet.
- *Know this:* in your 20-set test, Gemini passed both detectors on 12 of 20 sets and Humarin on 8 of 20. Humarin dropped two statistics; Gemini kept every statistic but repeated citations. So "Humarin first" is a choice for local and free, not because it is stronger.
- *Check with your supervisor* what exactly their reason was. It is not written anywhere.

**The guard is deterministic, not a meaning model** *(you decided: no NLI)*
- *Why:* a rewrite with the lowest score could be wrong (`higher risk` became `lower rate … [citation needed]`) and was still inserted.
- *What it checks:* citations, years and numbers (including minus signs) kept; no invented markers; negation not added or removed; direction not flipped (higher/lower, increase/decrease…); brackets balanced; length between 0.4 and 2.2 times the original; no `,.` `;.` `..` or space inside brackets.
- *Limit:* it cannot prove that a paraphrase keeps its meaning. It only catches the failures on its list. You decided to **keep it as it is**.

**The lowest safe score wins, even if it only barely helps** *(you decided; the 0.15 margin rule was removed)*
- *Consequence:* a badge can read "Tier 2 · T5 · 1.00": the rewrite scored 0.9996 against 1.0000 and both show as 1.00. The score is right, only the display rounds it. See `OPEN_ISSUES.md` (B8).

**A sentence with a citation goes to Gemini only** *(you decided: "option A")*
- *Why (measured on 40 cited sentences):* Humarin kept every citation in 42% of its candidates (19 of 40 sentences had at least one), T5 in 70% (30 of 40). Gemini follows instructions and keeps the marker.
- If Gemini is not available or gives nothing safe, the original is kept with a reason. No local fallback for cited sentences.

**A non-default style tries Gemini first** *(you decided, 22 Oct)*
- *Why:* only Gemini applies the style (a line in its prompt). Humarin and T5 ignore it, and the rule-based rewriter only adds a pronoun for non-academic styles. If the style choice is to mean anything, Gemini has to go first.
- *Fallback:* if Gemini gives nothing usable, the local tiers still run (the style is then ignored).
- *Know this:* the style is one line of the prompt, so the six styles may produce similar rewrites. A stronger per-style prompt would be a separate step.

**Gemini uses one model, `gemini-3.8-flash` (`GEMINI_MODEL`)** *(your decision)*
- The old code tried five model names one after another; failures cost 5 to 9 seconds each.
- A short 429 is retried twice with a 2 s back-off. A "daily quota used up" answer is **not** retried: Gemini is skipped for 5 minutes and the next tier answers. The key to use is the paid one (`GOOGLE_API_KEY_PAID`), which the code prefers.

**T5: every version it writes is scored** *(you approved)*
- New function `paraphrase_candidates()`; the old `paraphrase_sentence()` behaves as before. Often only 1 or 2 of T5's 3 versions differ from the original, so the gain is small. T5 uses 3 beams (was 4) with the same results in tests.

**Green and amber at 0.40** *(you approved)*
- A rewrite is a success (green) only if its own score is below 0.40; if the text changed but the score is 0.40 or more, it is only an attempt (amber).

**Style, in short.** Only Gemini applies it (see above). This is why the style list is one fixed list of six; an unsupported style returns HTTP 400.

**Citations stay in the text the detector scores** *(you decided on 21 Oct; to confirm with your supervisor)*
- *Why:* a real detector reads the whole text, and flagging more sentences would spend extra Gemini calls on cited sentences.
- *Measured:* in a citation-dense paper (176 of 452 sentences cited) **184 sentences are flagged with the citations and 380 without**. In a thesis 996 → 1000, in two lighter papers 28 → 28 and 30 → 38.

**Ideas we tested and dropped**
- *"Make T5 return only 1 version."* 3 versions take 5.2 s and 1 version takes 5.2 s. The time goes into the search.
- *"Write one version at a time and stop when one is good."* The first Humarin version scored under 0.40 in 0 of 6 sentences, and one-at-a-time costs more.
- *Diverse beam search for Humarin.* Tested; results are in `DIVERSE_BEAM_RESULTS.md`. The code is on an archive tag, not on this branch.
- *Hiding citation markers from the models and putting them back afterwards.* Replaced by "citations go to Gemini only".

### 3.3 Numbers you can quote

| Measurement | Result |
|---|---|
| One click, 32-word sentence, Humarin and T5 both running | about 12 s (Humarin 5 s + T5 5.6 s + scoring 1.1 s). A request on a cold start took 13.4 s, warm 4.9 s (the models are now preloaded) |
| Humarin settings | 5 versions: 5.4 s · 1 version: 5.3 s · greedy (1 version, no search): 2.5 s |
| Gemini free key | "overloaded" errors, one call took 188 s, then "quota exceeded, limit 20" |
| Three simultaneous clicks | limit 1: results at 5.9 / 10.9 / 16.4 s; limit 3: 14.2 / 15.6 / 15.6 s. Same total, limit 1 gives the earliest first result |
| Local tiers on a citation-dense paper | Humarin keeps the meaning in about half of its useful rewrites; T5 is safe but barely changes the text; 6 of the rule-based tier's 8 lowering rewrites were broken text (`,.`), now fixed |
| Replay of 20 flagged sentences of one paper (local tiers only) | 8 rewritten and kept (7 below 0.40, 1 partial), 11 kept as original because no safe rewrite scored clearly lower, 1 was already human |
| Computer | i5-8250U laptop, 4 cores, no GPU |

### 3.4 Limits to mention
- Scores come from **one** detector (the local BERT model), not from ZeroGPT, Turnitin or Copyleaks.
- The guard does not check meaning beyond its list. Direct quotations are not protected yet (`OPEN_ISSUES.md` B7).
- The local models are weak on citation-dense text; Gemini carries those sentences.
- Gemini has not been run against the paid key yet; the routing and guard were tested with a fake Gemini.

---

## 4. Backend

**Already there:** a Flask server (`backend/app.py`) with the logic in `backend/aidetector/service.py`. Uploads are background jobs kept in memory.

### 4.1 What was built here

**A layout-aware document reader** (`pipeline/block_extractor.py` and `pipeline/structure.py`) — instead of one flat string:
- PDF paragraphs are rebuilt from line spacing, indents, short last lines, list markers and style changes; justified lines with wide gaps are re-joined; a heading above its paragraph is split off; a paragraph that continues on the next page is joined.
- Removed: running headers, page numbers, footnotes and footnote marks (small print in the lower 40% of the page), tables with and without borders (but never real paragraphs in a highlighted box), figure text, formula lines, captions, table-of-contents lines, rotated text, cover-page metadata, front matter before the abstract, and every reference list.
- DOCX uses real paragraphs and heading styles; TXT and pasted text use blank lines.
- Scanned PDFs, password-protected PDFs and the "protected document" placeholder stop with a plain message (`error_code`); partly scanned PDFs are read and a note says how many pages were skipped. **No OCR, by decision.**
- Checked on 9 real papers (a 28-page paper, a 112-page thesis, a 38-page review, a 7-page journal article, 2 physics papers, a German paper with footnotes, an AI review with a cover page, a protected file) and on generated PDFs. It is a set of heuristics with known gaps (`OPEN_ISSUES.md` B5).

**Sentences and scoring:** `sentences.py` (Punkt plus abbreviation rules), `text_cleaner.py` (only glued sentences get their space back; URLs, e-mails and DOIs are protected), `detector.py` (blocks of 4 consecutive sentences; `para` on every sentence; headings returned separately).

**Jobs and service:** the uploaded file is deleted right after it was read; it is stored as `<job id><ext>` (the client's name is never used); expired jobs and orphaned files are removed at start, on every upload and every 10 minutes; a document is cut to 20,000 words; the three models load in the background at start (`/api/health` reports `models_ready`); at most `MAX_CONCURRENT_HUMANIZE` (1) humanize requests use the models at once and at most `MAX_CONCURRENT_GEMINI` (2) Gemini calls are in flight.

**Humanizer safety:** the guard, the routing and the decision rule (section 3).

**Earlier fixes (14 Oct):** one Gemini model; all T5 versions scored; the hyphen is kept when a word is split at a line end; no invented scores; missing requirements added; an unused T5 style argument removed.

### 4.2 Left alone on purpose

| Item | Why |
|---|---|
| Three API implementations (Flask and two FastAPI files, one of which cannot start) | Supervisor (21 Oct): leave it as it is for now |
| Insecure defaults (`debug=True`, open to the network, open CORS, fixed `secret_key`, no upload size limit) | Fine on a laptop; only matters when deployed |
| Whole-document rewrite (`/api/humanize`) | Out of scope; a "humanize all" loop exists in the colleague's frontend and uses the sentence call |
| OCR for scanned PDFs | By decision: no OCR; a soft message instead |
| Time limit on Gemini calls | Supervisor's pipeline; a paid key probably removes the need |

### 4.3 Problems we solved
- **Windows Smart App Control** blocked a PyTorch file (`WinError 4551`), so the backend could not start. You turned Smart App Control off.
- **Free Gemini key:** 20 requests a day. The fix is a paid key as `GOOGLE_API_KEY_PAID`.

### 4.4 The API is locked (22 Oct)
`API_FLOW.md` was given to the colleague who builds the new frontend. **Keys, routes and request fields are frozen; values may change.** Everything added on this branch (`para`, `headings`, `notes`, `error_code`, `models_ready`, `warmup`, `engine`, `failed`, `reason`) is already in that file. Unsupported styles now return HTTP 400 instead of silently becoming `academic` (a change from `main`).

---

## 5. Frontend

**Status.** The first test frontend (built on this branch in October) was replaced on 22 Oct by the colleague's frontend, merged from `main`: Next.js 13.5 (App Router), React 18, Tailwind 3, shadcn/ui, Zustand and framer-motion. **From now on no changes are made to the frontend from this side**; its owner is the colleague. The old one is kept outside the repo in `ReviewIt-Humanizer/ReviewIt-frontend-old`.

**What the new frontend uses from the backend:** `/api/detect-text`, `/api/detect` + `/api/status/<id>` + `/api/result/<id>` + `DELETE /api/status/<id>`, `/api/humanize-sentence` and `/api/health` (and `/styles`, which is not in `API_FLOW.md`). It reads `para`, `headings`, `notes`, `error_code`, `engine`, `failed`/`reason` and `models_ready`.

**What it does:** a Dashboard (paste or upload, Document and Checklist views with headings, filters, click-to-humanize with a style, revert, next/previous AI sentence, "Humanize all", Highlight/Compare), a Humanizer studio page (a text box, one `/api/humanize-sentence` call per sentence), History and Settings (in browser memory only), and a Plagiarism page and a credit counter with sample data.

**Things noticed when reading it** (no changes were made; see `OPEN_ISSUES.md` F2): the overall score is the average of the sentences' own scores; a "failed" rewrite is still marked rewritten; "Humanize all" always uses `academic`; the studio page shows a fixed latency number; there is no queue, so clicks run at the server's pace.

Frontend items from the first version (queue, "kept the original" message, amber states, model-loading banner) are fixed in `FIXED_ISSUES.md` (FF1 to FF10) but belong to the old frontend.

---

## 6. Code decisions (the "how")

**Backend**
1. `_generate_candidates()` returns `None` when nothing was tried or it failed, and `[]` when the model produced nothing usable. `paraphrase_sentence()` therefore returns exactly what it always did.
2. `paraphrase_candidates()` was added instead of changing `paraphrase_sentence()`, because other code calls the old one.
3. The humanizer's tiers are nested functions (`_tier_humarin`, `_tier_t5`, `_tier_gemini`) that share one running best candidate; the order is chosen in one place.
4. `check_candidate()` returns `(ok, reason)`; the last reason becomes the `reason` of a failed answer.
5. `_call_gemini` uses a semaphore, retries a short 429 and puts a 5-minute cool-down on a daily-quota 429.
6. The service raises an error for missing scores inside its existing error handling.
7. Model loaders (BERT, Humarin, T5, Gemini client) have a lock each, so parallel clicks cannot load a model twice.
8. Only `block_extractor.py` knows the layout; `structure.py` only sees blocks with text, size, bold, italic, page and position, so it can be tested without PDFs.
9. The rule-based splitter has its own joiner (`_join_sentences`) so it cannot produce `,.`.
10. The test and timing scripts that are not tests are kept out of the repository.

**Tests.** 217 tests (`backend/tests`, `python -m pytest tests -q`). They cover the reader (generated PDFs), structure, sentences, cleaner, guard, routing (with a fake Gemini), clean-up, styles and unreadable files. 21 tests run against real papers only when the PDFs are in `backend/test_papers/` (git-ignored). The models themselves and the Flask routes are not exercised.

---

## 7. Your contribution

**What you did**
- Set the goal and the rules: research-based fixes for every use case, no guessing, plan before building, check before claiming, no AI tag on new commits.
- Made the decisions listed above: guard stays deterministic and is kept; the lowest safe score wins; sentences with citations go to Gemini only; a non-default style tries Gemini first; skip Gemini on a used-up quota; no OCR (soft message); citations stay in the scored text; paid Gemini key for production; the API is locked for the colleague's frontend; no frontend changes from your side.
- Asked the questions that shaped the work: why only one rewrite passed, why it is slow, who added the guard, how to measure each fallback, whether titles over 40 words or short sentences break the reader.
- Tested in the browser and sent screenshots that exposed real bugs (prose removed as "tables", a footnote glued into a sentence, a bullet scrambled).
- Turned off Smart App Control and handled the Git side (merges, pushes, branches).

**How the code was made**
- Everything is committed under your name. This session's code was written with Claude Code as the coding assistant. The 18 commits from 14 Oct carry a `Co-Authored-By` tag; later commits do not.
- Your two earliest commits are yours. Say how you made them the way it really happened.

**A suggested answer**
> I set the requirements and made the design decisions: what to build and leave out, the thresholds, how a rewrite is chosen and kept, how citations and styles are routed. I tested it in the browser and reported the bugs that shaped the fixes. I integrated Humarin earlier. For the reader, the guard and the backend fixes I worked with Claude Code as my coding assistant.

Be ready to explain in your own words: the four rewriters and their order, why scores are per group of four, the guard and what it cannot do, why cited sentences go to Gemini, green versus amber, and the Gemini free-tier limit.

---

## 8. Stack and libraries

**Backend**

| Tool | Version | Used for |
|---|---|---|
| Python | 3.12.10 | Runtime |
| Flask, flask-cors | 3.1.3, 6.0.5 | The server and browser access |
| PyTorch (CPU) | 2.14.1 | Runs the local models |
| transformers | 5.19.0 | Loads BERT, Humarin and T5 |
| NLTK | 3.9.1 | Cutting text into sentences (Punkt) |
| PyMuPDF | 1.28.2 | Reading PDFs by layout |
| python-docx | 1.2.0 | Reading Word files |
| python-dotenv | 1.0.0 | Reading `backend/.env` |
| google-genai | 2.30.0 | Talking to Gemini |
| pytest (`requirements-dev.txt`) | 9.1.1 | The 217 tests |

**Frontend (colleague's)**

| Tool | Version |
|---|---|
| Next.js (App Router) | 13.5.1 |
| React | 18.2.0 |
| TypeScript | 5.2.2 |
| Tailwind CSS | 3.3.3 |
| shadcn/ui (Radix), Zustand 5, framer-motion 14, recharts, sonner, lucide-react | — |
| ESLint | 8.49.0 |

**Models**

| Model | Role | Chosen by |
|---|---|---|
| `followsci/bert-ai-text-detector` | Scores AI-ness; flags at 0.75 | Original code |
| `humarin/chatgpt_paraphraser_on_T5_base` | Rewriter 1 (default style) | You and your supervisor |
| `Vamsi/T5_Paraphrase_Paws` | Rewriter 2 | Original code |
| `gemini-3.8-flash` (`GEMINI_MODEL`) | Rewriter 3; the only one for cited sentences; first for non-default styles | Your supervisor's default |
| Rule-based code | Rewriter 4 (last resort, uncited only) | Original code |

---

## 9. Files we changed

**Backend (`backend/`)**
- `aidetector/pipeline/block_extractor.py` (new reader), `structure.py` (new: heading / body / drop), `sentences.py` (new), `candidate_guard.py` (new), `detector.py` (blocks of 4, `detect_document`), `text_cleaner.py`, `humanizer.py` (routing, guard, decision rule, Gemini limits), `restructuring_engine.py` (`_join_sentences`), `t5_humanizer.py` (`paraphrase_candidates`, load lock), `humarin_humanizer.py` (yours; load lock), `pdf_extractor.py` (hyphen).
- `aidetector/service.py` (jobs, clean-up, warm-up, limits, styles, errors), `aidetector/config/settings.py`, `app.py` (`/api/health`, `engine` copied).
- `tests/` (217 tests), `bench_concurrency.py`, `requirements-dev.txt`, `README.md`, `.gitignore` (`test_papers/`).

**Docs** (kept outside the repo in `ReviewIt-Humanizer/docs/ReviewIt-AI-Detector-Docs/`): `API_FLOW.md` (locked), `CODE_FLOW.md`, `PROJECT_WALKTHROUGH.md`, `OPEN_ISSUES.md`, `FIXED_ISSUES.md`, `DIVERSE_BEAM_RESULTS.md`.

**Frontend:** the colleague's `frontend/`; nothing is changed from this side.

---

## 10. Questions you may get

1. **Why Humarin first?** It runs locally and is free: no key, no quota, no internet. Gemini scored better in my 20-set test (12 of 20 against 8 of 20) and keeps facts better, so it carries cited sentences and non-default styles.
2. **Why do cited sentences only go to Gemini?** Measured: Humarin kept the citation in 42% of its versions and T5 in 70%; Gemini follows instructions and keeps it. A rewrite that loses a citation is thrown away by the guard anyway.
3. **How do you make sure a rewrite does not change the meaning?** A deterministic guard: citations, numbers, negation, direction of change, markers, punctuation. It cannot prove meaning is kept; it catches the failures on its list. If nothing safe beats the original, the original is kept and the answer says why.
4. **Why does a sentence sometimes show "No better rewrite · 0.00" and sometimes "· 1.00"?** The badge shows the sentence's own score. 0.00 means the sentence is already human on its own (it was red because of its block of 4); 1.00 means it is AI-like and nothing safe scored lower.
5. **How is the AI score worked out?** The detector scores blocks of 4 consecutive sentences and each sentence takes its block's score; a sentence is "AI" at 0.75 or more. The page's overall number is the average.
6. **What do green and amber mean?** Green: the rewrite scores below 0.40. Amber: the text changed but it still looks AI.
7. **What does the style do?** Only Gemini applies it. For any style other than `academic`, Gemini runs first; Humarin and T5 ignore the style.
8. **What does the document reader remove?** Title page, metadata, headers, page numbers, footnotes, tables, figures, formulas, captions and every reference list; headings are kept as headings. Scanned PDFs are not supported (a soft message), by decision.
9. **Why is rewriting slow?** The local rewriters take a few seconds on this laptop; the long waits came from the Gemini free key. A paid key and a GPU would fix it.
10. **What did you leave out, and why?** Whole-document rewrite, OCR, a Gemini time limit, an upload size limit, merging the three APIs, and quotation protection. Those are scope or supervisor decisions; all are in `OPEN_ISSUES.md`.
11. **What next?** Run against the paid Gemini key and measure again; protect direct quotations; decide the minimum-improvement rule for the badge; confirm with the supervisor whether citations stay in the scored text.

---

## 11. Words used here

- **Rewriter / engine:** one of Humarin, T5, Gemini or rule-based.
- **Block:** four sentences in a row that the detector scores together.
- **Detector:** the BERT model that gives a 0-to-1 AI score.
- **Guard:** the checks every rewrite must pass before it is scored or kept.
- **Humarin:** a paraphrasing model (`humarin/chatgpt_paraphraser_on_T5_base`).
- **Attempted:** rewritten, but the new score is still 0.40 or more.
- **Failed (`failed: true`):** no safe rewrite scored lower than the original, so the original is kept.
- **Heading / body / drop:** what the document reader decides for each block.
- **API call:** a message from the page to the server, sent to an address like `/api/detect-text`.
- **Job:** an upload being processed in the background, with its own id.
