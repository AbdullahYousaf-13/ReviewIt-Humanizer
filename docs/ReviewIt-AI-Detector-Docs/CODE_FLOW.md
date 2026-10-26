# What happens when someone uses the site — start to finish

Last updated 2026-10-26. This describes the code as it is on branch `abdullah/humanizer-dev` (the same as `main` plus later work). The frontend is the new one built by a colleague (Next.js 13, shadcn/ui, Zustand). The exact JSON of every call is in `API_FLOW.md`, which is locked: keys, routes and request fields do not change.

## The parts

- **The page** — the website you see. Code in `frontend/`. Opens at `http://localhost:3000`. It is the colleague's frontend; this project does not change it.
- **The server** — does the thinking. Code in `backend/`. Runs at `http://127.0.0.1:5000` (Flask, `backend/app.py`).
- **The detector** — a model (`followsci/bert-ai-text-detector`) that gives a piece of text a score from 0 (written by a human) to 1 (written by AI).
- **The document reader** — turns an uploaded file or pasted text into paragraphs and headings and throws away everything that is not body text (title page, references, tables…).
- **Four rewriters** — Humarin, T5, Gemini and a rule-based one. They try to rewrite a sentence so the detector scores it lower.
- **The guard** — checks every rewrite before it can be used (citations, numbers, negation, direction, broken punctuation).

The page and the server talk by sending small messages called **API calls**. Each has a web address, like `/api/detect-text`.

---

## The whole journey in 14 steps

1. You open the site and go to the **Dashboard**.
2. You paste text, or upload a PDF, Word or text file.
3. You click **Detect**.
4. The server reads the text as paragraphs and headings, cuts it into sentences and removes noise (uploads only).
5. The detector scores the sentences, in groups of four.
6. The page shows your document in paragraphs. Sentences are marked high AI (red), mixed (amber) or human.
7. You click a sentence and choose a style.
8. The page sends that sentence, with the sentences around it, to the server.
9. The server tries the rewriters in an order that depends on the style and on whether the sentence has a citation.
10. Every rewrite goes through the guard and is scored by the detector. The lowest safe score wins.
11. If nothing safe beats the original, the original is kept and the answer says so.
12. The page swaps the sentence, shows which rewriter won and the new score, and lets you revert.
13. You can switch to the **Compare** view (original and rewrite side by side).
14. You can click **Humanize all**, which does steps 7 to 12 for every high-AI sentence, one after the other.

The examples below use this text:

> Artificial intelligence has fundamentally transformed the landscape of modern education. It is important to note that these technologies offer numerous benefits for both students and educators. Furthermore, the integration of machine learning algorithms facilitates personalized learning experiences. Moreover, it is crucial to consider the ethical implications of such systems. My cat knocked a glass off the table yesterday and I laughed way too hard about it. We went to the lake after lunch because the weather finally cleared up.

---

## Scene 1 — You open the site

You type `http://localhost:3000`. `frontend/app/page.tsx` shows the landing page. The **Dashboard** is `frontend/app/dashboard/page.tsx` (with `layout.tsx`, a sidebar and a top bar).

The top bar (`components/dashboard/topbar.tsx`) calls `GET /api/health` every 8 seconds. It shows whether the backend is online and, while `models_ready` is `false`, that the models are still loading (the server loads the detector, Humarin and T5 in the background when it starts, about 30 seconds on a laptop CPU). The address of the backend is `NEXT_PUBLIC_API_BASE_URL`, default `http://127.0.0.1:5000` (`frontend/lib/api.ts`).

Other pages exist in the frontend (Humanizer studio, History, Plagiarism, Settings). The History and Settings data live only in the browser (Zustand store, lost on reload), and the Plagiarism page and the credit counter use sample data; none of that is connected to the backend.

---

## Scene 2 — You paste text or upload a file

The Dashboard has a text box (paste) and a file box (`file-upload-card.tsx`). Detect is sent from `handleDetect()` (paste) or `handleFileProcess()` (upload) in `app/dashboard/page.tsx`.

---

## Scene 3 — Detect a pasted text

```
POST http://127.0.0.1:5000/api/detect-text
{ "text": "Artificial intelligence has fundamentally transformed ..." }
```

What the server does (`backend/aidetector/service.py`, `detect_text_service()`):

1. `blocks_from_plain_text()` turns the text into blocks (blank lines are paragraph breaks).
2. `build_document(..., uploaded=False)` (`pipeline/structure.py`) marks each block as a heading or body text. Pasted text is the person's own, so nothing is dropped as noise: only headings and a trailing reference list are interpreted.
3. `detect_document()` (`pipeline/detector.py`):
   - cuts each paragraph into sentences (`pipeline/sentences.py`: NLTK Punkt plus rules for `et al.`, `Fig.`, `e.g.`, initials and citation-only pieces; pieces under 6 words are left out),
   - puts every 4 consecutive sentences in a **block** and gives the block a score from 0 to 1,
   - every sentence gets the score of its block, and the label `"ai"` when that score is **0.75 or more** (`DETECTION_THRESHOLD`), otherwise `"human"`,
   - every sentence carries `para` (its paragraph number); headings are returned separately with the paragraph they stand before.
4. The service adds a summary (counts, average score). The overall `label` is `"ai"` when the average is 40% or more.

What comes back (shortened, example values):

```json
{ "success": true, "score": 0.667, "score_pct": 67, "label": "ai",
  "sentences": [
    { "text": "Artificial intelligence has fundamentally ...", "label": "ai",    "score": 1.0,    "para": 0 },
    { "text": "It is important to note that ...",              "label": "ai",    "score": 1.0,    "para": 0 },
    { "text": "My cat knocked a glass off the table ...",      "label": "human", "score": 0.0001, "para": 0 } ],
  "headings": [],
  "summary": { "total_sentences": 6, "ai_sentences": 4, "score": 67 } }
```

Sentences 1 to 4 share one score (they are one block), and sentences 5 and 6 share another.

---

## Scene 4 — Detect an uploaded file

The page accepts `.pdf`, `.docx`, `.doc` and `.txt`.

1. `POST /api/detect` sends the file as a form upload. `create_detection_job()` checks the extension, saves the file as `backend/uploads/aidetector_uploads/<job id><ext>` (the client's file name is never used) and starts a background thread. It answers at once: `{ "job_id": "...", "status": "processing", "filename": "..." }`.
2. The page asks every 1.5 seconds: `GET /api/status/<job id>` → `processing`, `done` or `error` (with `elapsed_seconds`, `error` and `error_code`).
3. Meanwhile `_process_file_background()` runs:
   - **Read:** `extract_blocks_with_notes()` (`pipeline/block_extractor.py`) reads the file by layout: lines are merged into paragraphs from line spacing, indents, list markers and style changes. It removes running headers and page numbers, footnotes and footnote marks, tables (with and without borders), figures and their text, formula lines and rotated text. A paragraph that continues on the next page is joined. The uploaded file is **deleted right after it was read**.
   - **Unreadable files:** a fully scanned PDF, a password-protected PDF and the "protected document" placeholder stop the job with a plain message and an `error_code` (`scanned` or `protected`). A PDF with some scanned pages is read, and a note says how many pages were skipped. There is no OCR, by decision.
   - **Sort:** `build_document(..., uploaded=True)` (`pipeline/structure.py`) classifies every block: title page and cover metadata, front matter before the abstract, reference lists (cut at their heading or where the text looks like references), captions, table-of-contents lines and label-like fragments are dropped. Headings are kept as headings. A heading that sits directly above its paragraph or runs on in the same line is split off.
   - If fewer than 10 words are left, the job ends with the error "No usable text could be extracted…".
   - Only the first **20,000 words** are kept.
   - `detect_document()` scores it exactly as in Scene 3.
4. When the status is `done`, the page asks `GET /api/result/<job id>`: `sentences` (with `para`), `headings`, `notes`, `summary`, `filename`. Then the page asks the server to delete the job: `DELETE /api/status/<job id>`.

If a job or file is left behind (closed tab, restart), `cleanup_expired()` removes it: at start, on every upload and every 10 minutes (`RESULT_TTL` 1 hour, `CLEANUP_INTERVAL` 10 minutes).

---

## Scene 5 — The page shows the result

`initInteractiveSentences()` in `app/dashboard/page.tsx` builds one record per sentence: original text and score, current text and score, paragraph number, `isHumanized`, engine.

**You see**
- A gauge with the overall AI score, and "score before → score now" once something was rewritten. The page computes it as the average of the sentence scores (`currentOverallScore`).
- The sentence breakdown (`components/dashboard/sentence-breakdown.tsx`): a **Document** view (paragraphs, with headings above them) and a **Checklist** view, filter pills (all, high AI at 0.75 or more, mixed from 0.40 to 0.75, human below 0.40, rewritten) and a highlight toggle.
- Document notes (an amber box) when the server sent `notes`, for example skipped scanned pages.
- A **Highlight / Compare** switch (`compare-view.tsx`).

---

## Scene 6 — You click a sentence and humanize it

You select a sentence, pick a style (academic, business, creative, casual, narrative or technical) and click Humanize. `handleHumanize()` sends the third call. It includes the current text of the sentence before and after, so the rewrite fits in. Those two are only background and are never changed.

```
POST http://127.0.0.1:5000/api/humanize-sentence
{ "text": "It is important to note that these technologies offer numerous benefits ...",
  "style": "academic",
  "context_before": "Artificial intelligence has fundamentally transformed ...",
  "context_after":  "Furthermore, the integration of machine learning ..." }
```

Note: the page sends the **original** text of the sentence (not an earlier rewrite), so clicking again starts over from the original.

---

## Scene 7 — The server rewrites the sentence

This is the main part of the project (`pipeline/humanizer.py`, `humanize_single_sentence_smart()`).

**In the service** (`humanize_sentence_service()`):
1. Empty text → HTTP 400.
2. `resolve_style()`: an empty style means `academic`; a style that is not one of the six returns HTTP 400.
3. At most `MAX_CONCURRENT_HUMANIZE` requests (default 1) use the models at once; the others wait their turn.

**In the humanizer**
1. The original sentence is scored alone. This is the score to beat.
2. The routing decides which rewriters run and in what order:

| Sentence | Order |
|---|---|
| Has a citation (`[12]`, `(Smith et al., 2019)`) | **Gemini only.** The local models drop the marker about half of the time (measured). If Gemini is not available (no key, quota used up, cool-down) or gives nothing safe, the original is kept and the answer says why. The rule-based rewriter is never used for it. |
| No citation, style `academic` (or empty) | Humarin → T5 → Gemini → rule-based |
| No citation, any other style | Gemini → Humarin → T5 → rule-based. Only Gemini applies a style (a line in its prompt); Humarin and T5 ignore it. |

The first rewriter always runs. The next one runs only if nothing has helped yet or the best score is still **0.40 or more**.

3. What each rewriter does:

| Rewriter | Where it runs | Versions | Notes |
|---|---|---|---|
| Humarin | your computer | 5 | the paraphrase model `humarin/chatgpt_paraphraser_on_T5_base`, beam search |
| T5 | your computer | up to 3 | `Vamsi/T5_Paraphrase_Paws`; often only 1 or 2 differ from the original |
| Gemini | Google, over the internet | 3, then 3 simpler ones if the best is still 0.35 or more | model `GEMINI_MODEL` (default `gemini-3.8-flash`), key `GOOGLE_API_KEY_PAID` or `GEMINI_API_KEY`; gets the style and both neighbour sentences; at most `MAX_CONCURRENT_GEMINI` (2) calls at once; a short 429 is retried twice with 2 s back-off; a "daily quota used up" answer is not retried and Gemini is skipped for 5 minutes |
| Rule-based | your computer | 1 | plain code that swaps words and splits sentences; last resort, only if nothing has helped or the best is still 0.50 or more; never for cited sentences |

4. **Every candidate goes through the guard first** (`pipeline/candidate_guard.py`). A candidate is rejected if it: loses or changes a citation, a year or a number (a minus sign counts); adds a marker like `[citation needed]`; adds or removes a negation; flips a direction (higher/lower, increase/decrease…); has unbalanced brackets, a length outside 0.4 to 2.2 times the original, or a punctuation glitch (`,.`, `;.`, `..`, a space inside brackets). A rejected candidate is never scored and never kept.
5. Candidates that pass are scored by the detector. The **lowest score wins**, but only if it is lower than the original's score.
6. The winner is cleaned up (spacing, capital letter, final stop).
7. If no safe candidate scored lower than the original, the original is returned with `engine: "original"`, `failed: true` and a `reason` (for example "no rewrite scored lower than the original"). If the original was already below 0.40, nothing is reported as failed.

What comes back (example values; the full shape is in `API_FLOW.md`):

```json
{ "success": true,
  "data": { "original": "...", "humanized": "These technologies offer ...",
            "original_score": 0.9999, "new_score": 0.7703, "improvement": 0.2296,
            "engine": "t5", "failed": false, "reason": "" },
  "processing_time": 4.8,
  "humanized": "These technologies offer ...", "new_score": 0.7703,
  "original_score": 0.9999, "improvement": 0.2296, "engine": "t5" }
```

On a CPU-only laptop one click takes a few seconds (measured: 4.9 s warm, 13.4 s on a cold start before the models were preloaded). A slow Gemini call can add more.

---

## Scene 8 — The page updates the sentence

`handleHumanize()` in `sentence-breakdown.tsx` replaces the sentence's current text with `humanized`, its current score with `new_score`, stores the engine and shows a toast. If `data.failed` is `true` it shows "Humanization limited" with the `reason`. The sentence has an **engine badge** (`engine-badge.tsx`) and a **Revert to original** button that puts back the original text and score.

The score shown for a sentence is its own single-sentence score. The detector scored the sentence on its own here, but the red/amber/green colour at detection came from the block of 4. That is why a sentence can be red and still have a low single-sentence score. See `OPEN_ISSUES.md`.

---

## Scene 9 — Humanize all, and the Compare view

- **Humanize all** (`handleHumanizeAll()` in the dashboard page) takes every sentence with a score of 0.75 or more that is not yet rewritten and calls `/api/humanize-sentence` for each, one after the other, with the current neighbours as context, always with style `academic`. A failed call is skipped. There is no new backend call for it: it is the same click-to-humanize call repeated.
- **Compare** (`compare-view.tsx`) shows original and rewrite side by side. It uses what the page already has in memory; no call is made.

---

## Scene 10 — The Humanizer studio page

`app/dashboard/humanizer/page.tsx` has a plain text box. It cuts the text into sentences in the browser (a regular expression), calls `/api/humanize-sentence` for each sentence in turn with its neighbours as context, joins the results and shows the average score before and after. The "latency" it shows is a fixed number in the page, not measured.

---

## Scenes that do not call the server

Revert, filters, the view switches, Compare, History and Settings.

---

## When something goes wrong

| What happens | What you see |
|---|---|
| The backend is not running | The top bar shows it offline; calls fail with an error toast |
| Gemini is down, out of quota or has no key | Uncited sentences are still rewritten by Humarin or T5; **cited sentences are kept as they are** with a reason (`failed: true`) |
| No rewrite is safe and better | The original is returned (`engine: "original"`, `failed: true`, with `reason`); the page shows "Humanization limited" |
| A scanned or protected file | The job ends with `error_code` `scanned` or `protected` and a plain message |
| A partly scanned PDF | The result has `notes`; the page shows them in an amber box |
| A document over 20,000 words | Only the first 20,000 words are analysed (the response does not say so) |
| Two humanize requests at once | The second waits until the first is done (`MAX_CONCURRENT_HUMANIZE`) |

---

## Where to find things

| You want to see… | Open |
|---|---|
| The Dashboard: detect, upload, humanize all | `frontend/app/dashboard/page.tsx` |
| Sentence list, filters, click-to-humanize, revert | `frontend/components/dashboard/sentence-breakdown.tsx` |
| Side-by-side view | `frontend/components/dashboard/compare-view.tsx` |
| The calls to the server | `frontend/lib/api.ts` (types in `frontend/types/index.ts`) |
| Backend health in the top bar | `frontend/components/dashboard/topbar.tsx` |
| The server's addresses | `backend/app.py` |
| What each address does, jobs, clean-up, warm-up | `backend/aidetector/service.py` |
| Reading files (layout) | `backend/aidetector/pipeline/block_extractor.py` (PDF, DOCX and TXT; `pdf_extractor.py` only supplies the plain-text reader and serves the two old FastAPI apps) |
| Deciding heading / body / drop | `backend/aidetector/pipeline/structure.py` |
| Sentences and scoring | `backend/aidetector/pipeline/sentences.py`, `detector.py` |
| The rewriters and the routing | `backend/aidetector/pipeline/humanizer.py`, `t5_humanizer.py`, `humarin_humanizer.py` |
| The guard | `backend/aidetector/pipeline/candidate_guard.py` |
| Settings (thresholds, styles, limits) | `backend/aidetector/config/settings.py` |
| Keys and model name | `backend/.env` |
| Tests (217) | `backend/tests/` (run `python -m pytest tests -q`) |
