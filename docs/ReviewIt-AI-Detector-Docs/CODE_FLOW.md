# What happens when someone uses the site — start to finish

Last updated 2026-10-29. This describes the code on branch `abdullah/humanizer-new-engine`. The frontend is the colleague's Next.js app (shadcn/ui, Zustand); a few files in it were changed on this branch (listed in `PROJECT_WALKTHROUGH.md`). The JSON of every call is in `API_FLOW.md`: keys, routes and request fields are locked, only values may change.

## The parts

- **The page** — the website. Code in `frontend/`, opens at `http://localhost:3000`.
- **The server** — Flask, `backend/app.py`, at `http://127.0.0.1:5000`. Sign-up and login use a separate Node service (`nodeBackend/`, default `http://localhost:5001`) that is not part of this server.
- **The detector** — `followsci/bert-ai-text-detector`, a model that scores text from 0 (human) to 1 (AI).
- **The document reader** — turns an upload or pasted text into paragraphs and headings and drops everything that is not body text.
- **Four rewriters** — Gemini, Humarin, T5 and a rule-based one.
- **The guard** — checks every rewrite before it can be scored or shown.

---

## The journey in 12 steps

1. You open the Dashboard, paste text or upload a PDF, Word or text file, and click Detect.
2. The server reads the text as paragraphs and headings, cuts it into sentences and scores them in blocks of 4.
3. The page shows the document in paragraphs. Sentences are red (high AI), amber (mixed), or plain (human).
4. You click a sentence, choose a style and click **Humanize This Sentence**.
5. The page sends the sentence, its neighbours and its first-scan score to the server.
6. The server decides which rewriters run (table in Scene 6).
7. Gemini writes 5 rewrites in one call (JSON). If none reaches 30% or below, it is asked once more for 2 rewrites.
8. Humarin, T5 and rule-based run next to it when the sentence has no citation and the style is Academic.
9. Every rewrite goes through the guard, then is scored by the detector.
10. The page shows the best one as **Recommended** and the others as **Options**. The sentence turns green.
11. You can pick another option, or revert to the original.
12. **Humanize All** repeats steps 4–10 for every flagged sentence, one after the other.

The examples use this text:

> Artificial intelligence has fundamentally transformed the landscape of modern education. It is important to note that these technologies offer numerous benefits for both students and educators. Furthermore, the integration of machine learning algorithms facilitates personalized learning experiences. Moreover, it is crucial to consider the ethical implications of such systems. My cat knocked a glass off the table yesterday and I laughed way too hard about it. We went to the lake after lunch because the weather finally cleared up.

---

## Scene 1 — You open the Dashboard

`frontend/app/dashboard/page.tsx` is the page. The top bar (`components/dashboard/topbar.tsx`) calls `GET /api/health` every 8 seconds: it shows whether the backend is online and, while `models_ready` is `false`, that the models are loading (the server loads the detector, Humarin and T5 in the background when it starts). The backend address is `NEXT_PUBLIC_API_BASE_URL` (default `http://127.0.0.1:5000`, `frontend/lib/api.ts`). Humanize and Humanize All ask you to sign in first (the colleague's login).

---

## Scene 2 — Detect pasted text

```
POST /api/detect-text
{ "text": "Artificial intelligence has fundamentally transformed ..." }
```

On the server (`service.py`, `detect_text_service()`):
1. `blocks_from_plain_text()` makes blocks (a blank line is a paragraph break). `build_document(..., uploaded=False)` marks headings; pasted text is never judged as noise.
2. `detect_document()` (`pipeline/detector.py`) cuts every paragraph into sentences (`pipeline/sentences.py`; pieces under 6 words are left out), puts every **4 consecutive sentences** in a block and scores the block. **Every sentence gets its block's score.** A sentence is labelled `ai` at **0.75 or more**.
3. The service adds a summary. The overall `label` is `ai` at 30% or more (the "par score", `PAR_SCORE` = 0.30).

Each sentence in the answer has `text`, `label`, `score` and `para` (its paragraph number); headings come in a separate list.

---

## Scene 3 — Detect an uploaded file

The page accepts `.pdf`, `.docx` and `.txt` (old `.doc` files are rejected with a plain message).

1. `POST /api/detect` sends the file. The server saves it as `backend/uploads/aidetector_uploads/<job id><ext>`, starts a background thread and answers `{ job_id, status: "processing" }`.
2. The page asks `GET /api/status/<job id>` every 1.5 s until it is `done` or `error`.
3. The background job:
   - **Read:** `extract_blocks_with_notes()` (`pipeline/block_extractor.py`) rebuilds paragraphs from the layout. It removes running headers, page numbers, footnotes, tables, figures, formulas and captions, and joins a paragraph that continues on the next page. The file is **deleted right after it is read**.
   - **Unreadable files:** a scanned PDF, a password-protected PDF and the "protected document" placeholder stop with a plain message and an `error_code` (`scanned` or `protected`). A partly scanned PDF is read and a note says how many pages were skipped. There is no OCR.
   - **Sort:** `build_document(..., uploaded=True)` (`pipeline/structure.py`) decides for every block: heading, body or drop (title page, front matter, reference lists, captions, table-of-contents lines, back matter such as "The author declares no conflict of interest").
   - Fewer than 10 words left → error. Only the first 20,000 words are kept.
   - `detect_document()` scores it as in Scene 2.
4. `GET /api/result/<job id>` returns `sentences`, `headings`, `notes` and `summary`; then the page calls `DELETE /api/status/<job id>`. Expired jobs and orphaned files are removed at start, on every upload and every 10 minutes.

---

## Scene 4 — The page shows the result

`initInteractiveSentences()` builds one record per sentence (original and current text and score, paragraph, `isHumanized`, `options`).

- **Gauge and bar:** the overall AI score and the AI / Mixed / Human percentages of the document.
- **Sentences:** a **View** tab (document with paragraphs and headings, plus a Checklist layout) and a **Compare** tab (original and rewrite side by side). Filter pills: all, AI flagged (75% or more), mixed (30% to below 75%), human, rewritten. A **Highlights** switch turns the colours on and off.
- **Badges:** "High AI Risk", "Mixed Phrasing", "Human Written", "Humanized". The page shows **no per-sentence percentages**.
- **A humanized sentence counts as human** in the counts, the filters and the ratios (it is shown green), whatever its own score is. In the overall score it counts at no more than 30%.
- **Notes:** an amber box for document notes (skipped scanned pages).

---

## Scene 5 — You click a sentence and humanize it

```
POST /api/humanize-sentence
{ "text": "...", "style": "academic",
  "context_before": "...", "context_after": "...", "original_score": 0.98 }
```

The page sends the **original** text of the sentence (so a second click starts again from the original), the current text of its neighbours, and `original_score`: the score the first scan gave it (its block score). When it is sent, the server uses it and does not score the original again.

---

## Scene 6 — The server rewrites the sentence

`humanize_sentence_service()` returns HTTP 400 for empty text or a style that is not one of the six; an empty style means `academic`. At most `MAX_CONCURRENT_HUMANIZE` (1) requests use the models at once. Then `humanize_single_sentence_smart()` (`pipeline/humanizer.py`):

| Sentence | Who runs |
|---|---|
| Has a citation (`[12]`, `(Smith et al., 2019)`, or a name followed by "et al.") | **Gemini only**, because the local models drop the marker about half of the time |
| No citation, style `academic` | **Gemini, and next to it Humarin → T5 → rule-based** (two threads) |
| No citation, any other style | **Gemini only**, because only Gemini applies a style |

**Gemini** (`gemini_prompt.py`, model `GEMINI_MODEL`, default `gemini-3.8-flash`): one prompt and a system instruction. The system instruction holds the HARD RULES (same meaning, same strength, add nothing, keep exact); the prompt holds the style, the neighbour sentences, the target and eight short writing rules. The answer is JSON.
- **First call: 5 rewrites.** If none of them reaches the par score (30% or below), **one retry: 2 more rewrites**. The retry prompt shows Gemini its earlier attempts and why some were rejected, and asks for clearly different ones.
- A short rate-limit answer is retried twice with a 2 s back-off. A "daily quota used up" answer is not retried: Gemini is skipped for 5 minutes. Calls in flight are limited to `MAX_CONCURRENT_GEMINI` (2). Every call logs its time, tokens and cost.

**Local engines:** Humarin writes 5 versions, T5 up to 3, the rule-based one 1. Each engine keeps its lowest-scoring safe rewrite.

**The guard** (`pipeline/candidate_guard.py`) runs on every rewrite of every engine; a rejected rewrite is never scored or shown. It rejects a rewrite that:
1. is empty or identical to the original;
2. loses or changes a citation, a year or a first author, or repeats or adds a citation;
3. loses or changes a number (a minus sign counts);
4. adds invented text (`[citation needed]`, "Here is…");
5. has unbalanced brackets or a punctuation glitch (`,.`, `;.`, `..`, a space inside brackets);
6. is cut off, or is shorter than 0.4 or longer than 2.2 times the original;
7. adds or removes a negation;
8. adds a stock machine phrase (utilize, furthermore, crucial, enhance…);
9. splits a sentence that has a citation into two or more sentences;
10. adds a bracketed phrase with new words, or an acronym the original lacks;
11. adds a cause the original does not state ("caused", "led to", "made … more likely");
12. flips the direction of the claim (higher↔lower, increase↔decrease…).

The same rules for Gemini are also in its prompt, so it avoids them instead of losing a good rewrite. The guard's main job is to catch Humarin, T5 and rule-based, which cannot be instructed.

**What is shown, and in what order** (every rewrite below is already safe and scored):
- Gemini's best rewrite when it beats the original; Gemini's second best only at 30% or below.
- A Humarin, T5 or rule-based rewrite only at 30% or below **and** below the original (lower score first).
- Gemini's rewrites come first while one of them is at 30% or below; if none is but a local one is, the local one goes first.
- **Last resort:** if nothing beats the original but Gemini has a safe rewrite, its best one is shown anyway, even at 100%, so the page is never left empty.
- Only when Gemini has no safe rewrite at all (all rejected, or the call failed) does the original come back, with `engine: "original"`, `failed: true` and a reason.

The answer carries `humanized`, `engine`, `new_score`, `original_score`, `improvement`, `failed`, `reason` and `alternatives` (the other rewrites, in display order). A click takes 4–35 s on a CPU laptop (mean 12.7 s in a 26-sentence run): uncited sentences are slower because Humarin and T5 run next to Gemini; cited sentences take 6–10 s.

---

## Scene 7 — The page updates the sentence

`handleHumanize()` (`sentence-breakdown.tsx`) calls `humanizedFields()` (`frontend/lib/humanize.ts`):
- If the answer holds a rewrite (not `failed`, engine not `original`) the sentence turns green and a **rewrite box** (`rewrite-box.tsx`) opens: the original struck through, then **Recommended** and **Option 1…** with a **Use this** button. No engine names, no percentages.
- If nothing was kept, the sentence stays as it was and no popup opens.
- **Revert to original** puts back the original text.

---

## Scene 8 — Humanize All, Compare, the studio page

- **Humanize All** (`handleHumanizeAll()` in the dashboard page) takes every sentence at 75% or more that is not humanized yet and calls `/api/humanize-sentence` for each, one after the other, with the selected style. A failed call is skipped. There is no separate backend call for it.
- **Compare** shows original and rewrite side by side from the page's memory; no call is made.
- **Humanizer studio** (`app/dashboard/humanizer/page.tsx`) cuts a pasted text into sentences in the browser and calls the same endpoint per sentence.
- History, Settings, the credit counter and the Plagiarism page use local or sample data.

---

## When something goes wrong

| What happens | What you see |
|---|---|
| The backend is not running | The top bar shows it offline; calls fail with a message |
| Gemini is down, out of quota or has no key | Uncited sentences in Academic style are still rewritten by Humarin or T5; cited sentences and other styles come back unchanged with a reason |
| No rewrite beats the original | Gemini's best safe rewrite is still shown (last resort) |
| Gemini has no safe rewrite either | The sentence stays as it was; the answer has `failed: true` |
| A scanned or protected file | A plain message (`error_code` `scanned` or `protected`) |
| A partly scanned PDF | The result has `notes`, shown in an amber box |
| A document over 20,000 words | Only the first 20,000 words are analysed (the response has no flag for it) |
| Two humanize requests at once | The second waits for the first |

---

## Where to find things

| You want to see… | Open |
|---|---|
| Detect, upload, Humanize All, the panel | `frontend/app/dashboard/page.tsx` |
| Sentence list, filters, click-to-humanize, revert | `frontend/components/dashboard/sentence-breakdown.tsx` |
| Recommended and Options box | `frontend/components/dashboard/rewrite-box.tsx` |
| What the page does with an answer | `frontend/lib/humanize.ts` |
| Side-by-side view | `frontend/components/dashboard/compare-view.tsx` |
| Calls to the server | `frontend/lib/api.ts` (types in `frontend/types/index.ts`) |
| The par score on the page | `frontend/lib/par.ts` |
| The server's addresses | `backend/app.py` |
| Jobs, clean-up, warm-up, styles, limits | `backend/aidetector/service.py` |
| Reading files | `backend/aidetector/pipeline/block_extractor.py` |
| Heading / body / drop | `backend/aidetector/pipeline/structure.py` |
| Sentences and scoring | `backend/aidetector/pipeline/sentences.py`, `detector.py` |
| Which rewriters run, what is shown | `backend/aidetector/pipeline/humanizer.py` |
| What Gemini is told | `backend/aidetector/pipeline/gemini_prompt.py` |
| The guard | `backend/aidetector/pipeline/candidate_guard.py` |
| Thresholds, styles, limits | `backend/aidetector/config/settings.py` |
| Keys and model name | `backend/.env` |
| Tests (370) | `backend/tests/` (`python -m pytest tests -q`) |
