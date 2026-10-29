# Project walkthrough — ReviewIt humanizer

Last updated 2026-10-29. Work was done on `abdullah/humanizer-dev` (until 22 Oct) and on `abdullah/humanizer-new-engine` (from 26 Oct). The original project (the detector, the first humanizer and the Flask API) was already there and is described only as the starting point. The frontend is a colleague's app; this note says which of its files were changed on our branch.

---

## 1. The project in one minute

**What the app does.** You paste text or upload a document. The app reads it as paragraphs and headings, marks the sentences that look AI-written, and lets you click a sentence to rewrite it so that a detector scores it lower, without changing its facts. Each click gives one **Recommended** rewrite and up to three **Options**. You can pick another one, revert, or run **Humanize All** on every flagged sentence.

**If someone asks "what did you do?"**

> The backend already had a detector and a humanizer. I made it **safe and structured**: uploads are read by layout (title page, references, tables, footnotes removed) into paragraphs and headings; every rewrite goes through a **guard** (citations, numbers, negation, direction, causes, added text, broken punctuation); a failed rewrite is never inserted. I rebuilt the humanize click around **Gemini as the main engine** with a carefully designed prompt (hard meaning rules, one call of 5 rewrites and one retry of 2 that shows the earlier attempts), and kept Humarin, T5 and a rule-based engine as local options. Sentences with citations go to Gemini only, other styles go to Gemini only, and a sentence never comes back empty. I measured the pipeline on real papers: on a full paper the number of red sentences went from 24 to 4 (mean score 19% to 3%). There are 370 tests. The API shapes are locked for the colleague's new frontend.

---

## 2. What changed

**Before:** Gemini was tried first with a model list, then T5 and rule-based; the lowest score won even when the rewrite was wrong; uploads were read as one flat string.

**Now:**
- A layout-aware document reader with headings, paragraphs and soft errors for unreadable files.
- A 12-group guard on every rewrite, the same for every engine.
- One Gemini prompt (system instruction with HARD RULES, JSON answer), first call 5 rewrites, one retry of 2.
- Three results per click: Gemini first, then Humarin and T5 as options (only at 30% or below), rule-based as a last local option.
- A last resort: when nothing beats the original, Gemini's best safe rewrite is still shown.
- The API tells the page the winner, paragraphs, headings, notes, `failed` / `reason` and `alternatives`.

| Date | Commits | What |
|---|---|---|
| 13–16 Oct | `0d9384f` … `7573adb` | Humarin module and pipeline; first test frontend; backend fixes; first docs |
| 19–20 Oct | `fc70ada`, `1c7a61d`, `387cef7`, `1147eed`, `f4b6696` | Paragraph and heading reader, the first guard, upload clean-up, model warm-up, request limit, skip Gemini on a used-up quota |
| 21 Oct | `96d6f3f`, `fde1cd8`, `81d5b42`, `8c9fa56`, `f9fd756` | Lowest safe score wins, layout fixes found on real papers, soft errors for scanned files, citations → Gemini only |
| 22 Oct | `6c6249a` … `2ab077a`, `baf13ba` | Docs and old frontend out of git, colleague's frontend merged, non-default style tries Gemini first |
| 26–28 Oct | `5d364cd`, `aac109a`, `4149432`, `df21b50`, `c4bdaa4`, `446c50b`, `6cd0592`, `be90e61` | Single Gemini prompt with system instruction and JSON answer, three results per click, par score 30%, retry with the earlier attempts shown, stock-phrase guard, cost and time log |
| 28–29 Oct | `1974540`, `4dabe15`, `a603eef`, `f2a52ae`, `e3ec622`, `f543cfe`, `a164e4e`, `cd4ead0`, `7a8bef2`, `70bb3f0`, `a1d0bce` | Prompt fixes (strength, lists, "Name et al."), first call 5 and retry 2, a cited sentence stays one sentence, guard: added bracket / acronym / cause, last resort, frontend: no percentages or tags, counts follow green, "View" tab, neutral test examples |

---

## 3. AI / ML side

### 3.1 How one click works
1. Routing: a sentence with a citation, or any style other than Academic, goes to Gemini alone. An uncited Academic sentence runs Gemini and, next to it, Humarin → T5 → rule-based.
2. Gemini writes 5 rewrites. If none is at 30% or below it writes 2 more, seeing the earlier attempts and why some were rejected.
3. Every rewrite passes the guard, then is scored by the detector.
4. Gemini's best is shown if it beats the original (its second only at 30% or below); local rewrites only at 30% or below and below the original. If nothing beats the original, Gemini's best safe rewrite is shown anyway.

Numbers to remember: **0.75** = the detector calls a sentence AI (red). **0.30** = the "par score": below it a sentence counts as human; mixed is 0.30 to 0.75.

### 3.2 Decisions
- **Gemini is the main engine, the local engines are options.** Humarin and T5 cannot follow instructions, cannot keep a citation reliably (they kept every citation in 42% and 70% of their candidates on 40 cited sentences) and ignore the style. Gemini does all three.
- **A sentence with a citation, or a non-default style, goes to Gemini only.** If Gemini is not available the original is kept with a reason.
- **The guard is deterministic.** No meaning model. It catches the failures on its list; the rest depends on the prompt.
- **The guard's main job is the local engines.** Gemini is told the same rules in its prompt, so a good Gemini rewrite is not lost to a rule it was never given.
- **First call 5 rewrites, retry 2.** Measured on 26 sentences with the latest prompt: the chance that a call holds at least one rewrite at 30% or below is 43% with 1 rewrite, 62% with 2, 73% with 3 and 85% with 5. Five rewrites cost about the same per sentence as two plus a retry and are faster.
- **Par score 30%** (it was 40%). Green only below it.
- **Last resort:** never leave the page empty; Gemini's best safe rewrite is shown even at 100%.
- **A humanized sentence counts as human** in the page's counts and filters, and at no more than 30% in the overall score.
- **No per-sentence percentages and no engine tags on the page.**
- **No OCR** for scanned PDFs: a soft message. **Old `.doc` files are not supported.**
- **Citations stay in the text the detector scores**, because a real detector reads the whole text.
- **Gemini skipped for 5 minutes on a "daily quota used up" answer;** a short rate limit is retried twice.

### 3.3 The Gemini prompt
- **System instruction (HARD RULES):** same meaning (who does what to whom; a link is never a cause; "made", "caused" or "led to" never replace "showed" or "found"; a duty is never turned into an action; no added or removed negation; no reversed direction), same strength (need/should/may never become "must"; no stronger single word), add nothing (no new fact, person, group, bracketed phrase or acronym; no "we" unless the target has it), keep exact (numbers, names, citations once at the end of the claim; "Name et al." is a citation; a sentence with a citation stays one sentence).
- **User prompt:** the style block, the neighbour sentences, the target, eight short writing rules (restructure; any run of three or more items becomes clauses or an uneven split; verbs over noun forms without losing strength; no stock phrases; no machine patterns or a word repeated three times; vary the rhythm; length within 30%; the rewrites differ), and a final self-check.
- **Why it is built this way:** few precise rules are followed better than many; each rule answers a mistake seen in the tests; no example sentences (the model copies them); the hard rules come first (Google's prompting guide).

### 3.4 Numbers you can quote

| Measurement | Result |
|---|---|
| Full paper (139 sentences), 26 flagged sentences humanized | red sentences 24 → 4; mean score 19% → 3% (our detector) |
| One "Humanize all" run, 26 sentences | 33 Gemini calls (26 first calls, 7 retries), about **$0.057**, about 5 min 50 s, mean 12.7 s per click |
| Cost per Gemini call | about $0.0013–0.0026; about $0.0022 per sentence |
| Click time | 4–35 s; cited sentences 6–10 s; uncited 10–35 s (Humarin 5–16 s, T5 3–22 s, Gemini 3–10 s) |
| List and definition sentences (#28–#35) | all 18% or below when scored alone after the list rule |
| Per-rewrite hit rate (30% or below), Academic | 17% (earlier prompt) → 43% (latest 5-rewrite prompt) |
| Styles on the same sentences | Business, Creative, Casual and Narrative reach 30% about as often as Academic; Technical a little less often |
| Tests | 370 (`python -m pytest tests -q`) |

### 3.5 Limits to mention
- One detector only (the local BERT model), not ZeroGPT, Turnitin or Copyleaks.
- Blocks of 4 sentences share one score, so a sentence can be red because of its neighbours, or hidden in a low block. Scored alone, a few sentences stay high after humanizing (abstract-noun sentences such as "Researchers and educators need to understand the potential, opportunities and challenges…").
- The guard cannot catch every meaning change (a cause where the original says "showed", a new action, a small shift in strength); the prompt handles those.
- The prompt changes of 28–29 Oct were tested offline and on saved runs; they have not been measured on a fresh Gemini run.

---

## 4. Backend

**Already there:** a Flask server (`backend/app.py`), the logic in `backend/aidetector/service.py`, uploads as background jobs in memory.

**Built here**
- **Reader** (`block_extractor.py`, `structure.py`): PDF paragraphs from line spacing, indents and styles; headings split off; running headers, page numbers, footnotes, tables, figures, formulas, captions, front matter, reference lists and back matter removed; DOCX uses real paragraphs and heading styles; scanned and protected PDFs stop with a plain message. Checked on 9 real papers.
- **Detector** (`detector.py`): blocks of 4 consecutive sentences; `para` on every sentence; headings returned separately.
- **Humanizer** (`humanizer.py`, `gemini_prompt.py`, `candidate_guard.py`): routing, prompt, guard, result ordering, last resort, retry, cost and time log. Local engines have load locks. Gemini calls are limited to 2 at once.
- **Service:** the file is deleted right after it is read; stored as `<job id><ext>`; expired jobs and orphaned files removed at start, on every upload and every 10 minutes; models load in the background (`/api/health` reports `models_ready`); at most 1 humanize request uses the models at once; optional `original_score` in the humanize request.

**Left alone on purpose:** the two old FastAPI apps (one cannot start); insecure defaults for a deployment (`debug=True`, open CORS, no upload size limit); a whole-document rewrite in one request; OCR; a Gemini time limit.

**The API is locked** for the colleague's frontend: keys, routes and request fields do not change; values may.

---

## 5. Frontend

The colleague's frontend (Next.js 13, React 18, Tailwind 3, shadcn/ui, Zustand, framer-motion) replaced the first test frontend. From now on nothing is changed in it except on request. **Files changed on our branch:**
- `app/dashboard/page.tsx` — the humanizer panel, Humanize All, the overall score (a humanized sentence counts at no more than 30%), the counts, the **View** tab (was "Highlight").
- `components/dashboard/sentence-breakdown.tsx` — click-to-humanize, filters and counts that treat a humanized sentence as human, no per-sentence percentages.
- `components/dashboard/rewrite-box.tsx` — Original, Recommended and Options; no percentages, no tags.
- `components/dashboard/compare-view.tsx` — no per-sentence percentages.
- `lib/humanize.ts`, `lib/par.ts` — what the page does with an answer; the par score.

The colleague should be told about these before the branch is merged.

---

## 6. Code decisions (the "how")

1. One guard function, `check_candidate()`, for every engine. It returns `(ok, reason)`; the reason goes into the retry prompt.
2. The Gemini answer is JSON with a fixed number of rewrites (5 on the first call, 2 on the retry).
3. Engines run in two threads: Gemini (network) and the local engines (CPU), one after the other inside the second.
4. A Gemini rewrite is never word-swapped by the old clean-up; only spacing is fixed.
5. The humanizer keeps its pool of safe Gemini rewrites, so the last resort can show the best one.
6. Only `block_extractor.py` knows the layout; `structure.py` sees blocks with text, size, bold, italic, page and position.
7. Every prompt rule is checked by a test; every guard rule has tests with real failures and checks on saved rewrites for false rejections.
8. Test sentences are neutral (schools, remote work, software); real papers are only used by tests that skip when the PDFs are absent.

---

## 7. Your contribution

**What you did**
- Set the goals and the rules: research-based fixes for every use case, no guessing, plan before building, check before claiming, no AI tag on commits, docs only in `ReviewIt-Humanizer/docs`, the API locked, no frontend edits unless asked.
- Made the decisions in section 3.2 and the earlier ones: guard deterministic and kept, citations to Gemini only, the first call of 5 and retry of 2, par score 30%, last resort, no OCR, no `.doc`, no percentages on the page.
- Asked the questions that shaped the work (why a sentence is red, why only one rewrite passed, who added the guard, what the cost of a click is) and sent screenshots and logs that exposed real bugs.
- Handled the Git side (merges, pushes, branches) and the documentation.

**How the code was made:** everything is committed under your name. The code was written with Claude Code as the coding assistant. Your two earliest commits are yours; say how you made them the way it really happened.

**A suggested answer**
> I set the requirements and made the design decisions: what Gemini and the local engines each do, the thresholds, how a rewrite is chosen and kept, how citations and styles are routed, what the guard rejects. I tested it in the browser, reported the bugs that shaped the fixes and checked full papers end to end. For the reader, the prompt, the guard and the backend I worked with Claude Code as my coding assistant.

Be ready to explain in your own words: why Gemini is the main engine, why the guard exists and what it cannot do, why cited sentences go to Gemini only, why scores are per block of 4, what the 30% par score means, and what a click costs.

---

## 8. Stack and libraries

**Backend**

| Tool | Version | Used for |
|---|---|---|
| Python | 3.12.10 | Runtime |
| Flask, flask-cors | 3.1.3, 6.0.5 | The server |
| PyTorch (CPU) | 2.14.1 | Local models |
| transformers | 5.19.0 | BERT, Humarin and T5 |
| NLTK | 3.9.1 | Sentences (Punkt) |
| PyMuPDF | 1.28.2 | PDFs by layout |
| python-docx | 1.2.0 | Word files |
| google-genai | 2.30.0 | Gemini |
| pytest | 9.1.1 | The 370 tests |

**Frontend (colleague's):** Next.js 13.5.1, React 18.2, TypeScript 5.2, Tailwind 3.3, shadcn/ui (Radix), Zustand 5, framer-motion, recharts, sonner. Login and sign-up use a separate Node service (`nodeBackend/`).

**Models**

| Model | Role |
|---|---|
| `followsci/bert-ai-text-detector` | Scores AI-ness; red at 0.75, par 0.30 |
| `gemini-3.8-flash` (`GEMINI_MODEL`) | Main rewriter; the only one for cited sentences and non-default styles |
| `humarin/chatgpt_paraphraser_on_T5_base` | Local option (default style, no citation) |
| `Vamsi/T5_Paraphrase_Paws` | Local option |
| Rule-based code | Last local option |

---

## 9. Files we changed

- **Backend:** `pipeline/block_extractor.py`, `structure.py`, `sentences.py`, `candidate_guard.py`, `gemini_prompt.py`, `detector.py`, `text_cleaner.py`, `humanizer.py`, `restructuring_engine.py`, `t5_humanizer.py`, `humarin_humanizer.py`; `service.py`, `config/settings.py`, `app.py`; `tests/` (370 tests), `bench_concurrency.py`, `requirements-dev.txt`.
- **Frontend:** see section 5.
- **Docs** (outside the repo, in `ReviewIt-Humanizer/docs/ReviewIt-AI-Detector-Docs/`): `API_FLOW.md` (locked keys), `CODE_FLOW.md`, `PROJECT_WALKTHROUGH.md`, `OPEN_ISSUES.md`, `FIXED_ISSUES.md`, `TODO.md`, `DIVERSE_BEAM_RESULTS.md`, and the Gemini test reports.

---

## 10. Questions you may get

1. **Why Gemini first?** It follows instructions, keeps citations and applies a style; the local models do none of that reliably. They stay as options and for the cases where Gemini finds nothing.
2. **How do you make sure a rewrite keeps its meaning?** The prompt states the meaning rules; a deterministic guard rejects what it can check exactly (citations, numbers, negation, direction, added causes, added text). It cannot prove meaning is kept.
3. **How is a sentence flagged?** A BERT model scores blocks of 4 sentences; each sentence takes its block's score; 0.75 or more is red, 0.30 to 0.75 mixed.
4. **What does a click cost and take?** About $0.002 per sentence on the paid key (two calls when the retry is needed); 4–35 s on a CPU laptop, mostly the local engines.
5. **Why are cited sentences Gemini only?** The local models dropped the citation in more than half of their candidates.
6. **What happens when nothing beats the original?** Gemini's best safe rewrite is still shown (even at 100%); the original comes back only when Gemini has no safe rewrite.
7. **What does the style do?** Only Gemini applies it; for any style other than Academic only Gemini runs.
8. **What does the reader remove?** Title page, metadata, headers, page numbers, footnotes, tables, figures, formulas, captions, reference lists, back matter. Scanned PDFs are not supported (a soft message).
9. **What did you leave out, and why?** A whole-document rewrite in one request, OCR, `.doc` files, a Gemini time limit, merging the old API files.
10. **What next?** Measure the 28–29 Oct prompt changes on a fresh run; decide whether upload scoring should be faster (blocks sorted by length, all CPU cores).

---

## 11. Words used here

- **Engine:** Gemini, Humarin, T5 or rule-based.
- **Block:** four sentences in a row that the detector scores together.
- **Par score:** 30%; a sentence below it counts as human.
- **Guard:** the checks every rewrite must pass before it is scored or shown.
- **Last resort:** Gemini's best safe rewrite, shown when nothing beats the original.
- **Recommended / Option:** the rewrites shown for a click, in order.
- **Heading / body / drop:** what the document reader decides for each block.
- **Job:** an upload being processed in the background.
