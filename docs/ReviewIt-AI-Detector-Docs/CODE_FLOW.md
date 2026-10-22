# What happens when someone uses the site — start to finish

## The parts

- **The page** — the website you see. Code in `frontend/`. Opens at `http://localhost:3000`.
- **The server** — does the thinking. Code in `backend/`. Runs at `http://127.0.0.1:5000`.
- **The detector** — a model that gives a piece of text a score from 0 (written by a human) to 1 (written by AI).
- **Four rewriters** — Humarin, T5, Gemini and a rule-based one. They try to rewrite a sentence so the detector scores it lower.

The page and the server talk by sending small messages to each other. These messages are called **API calls**. Each one has a web address, like `/api/detect-text`.

---

## The whole journey in 16 steps

1. You open the site.
2. The page loads and shows an empty form.
3. You paste some text.
4. You click **Detect AI**.
5. The page sends your text to the server.
6. The server cleans the text and cuts it into sentences.
7. The server puts the sentences in groups of four. The detector scores each group.
8. The server sends the sentences and their scores back.
9. The page shows your text. Sentences that look like AI are red.
10. You click a red sentence.
11. The page sends that sentence, with the sentences around it, to the server.
12. The server tries the rewriters one by one until it finds a good rewrite.
13. The server sends back the best rewrite.
14. The page swaps the sentence and colours it green or amber.
15. The page asks the server to score that group of four again and updates the score at the top.
16. You compare original and rewrite side by side, or you undo.

The same journey with a file upload is at the end.

The examples below use this text:

> Artificial intelligence has fundamentally transformed the landscape of modern education. It is important to note that these technologies offer numerous benefits for both students and educators. Furthermore, the integration of machine learning algorithms facilitates personalized learning experiences. Moreover, it is crucial to consider the ethical implications of such systems. My cat knocked a glass off the table yesterday and I laughed way too hard about it. We went to the lake after lunch because the weather finally cleared up.

---

## Scene 1 — You open the site

You type `http://localhost:3000` in the browser.

**What happens**
1. The browser asks the frontend for the page.
2. `frontend/src/app/layout.tsx` builds the frame of the page: the title and the fonts.
3. `frontend/src/app/page.tsx` runs on the frontend server first. It finds out where the backend lives. It reads the setting `API_URL` from `frontend/.env.local`. If the setting is missing, it uses `http://127.0.0.1:5000`.
4. It hands that address to the main part of the page, `frontend/src/components/Studio.tsx`.
5. `Studio` starts in your browser. It creates a helper for talking to the server (`createApi` in `frontend/src/lib/api.ts`). It also creates its memory: an empty list of sentences, the chosen style ("academic"), and which view is showing.

Nothing is sent to the server yet.

**You see:** the ReviewIt header, a card with two tabs (**Paste text** and **Upload file**), an empty text box, a Style dropdown and a grey **Detect AI** button.
**Files:** `Navbar.tsx` draws the header. `InputCard.tsx` draws the card.

---

## Scene 2 — You paste text

Whatever you type is kept in `InputCard.tsx`. The word and character counts update as you type. When the box has text, the **Detect AI** button turns blue. The **Try a sample** link fills the box with a sample paragraph.

The Style dropdown shows six styles: academic, business, creative, casual, narrative and technical. The list is in `frontend/src/lib/config.ts`.

---

## Scene 3 — You click Detect AI

**What happens in the page**
1. The button runs `submit()` in `InputCard.tsx`.
2. `submit()` calls `onDetectText(text)` in `Studio.tsx`.
3. That calls `start()`. `start()` clears the screen (old sentences, old errors) and cancels any earlier request. The button now says "Detecting…" and a **Cancel** link appears.
4. `start()` calls `api.detectText(text)` in `frontend/src/lib/api.ts`. This sends the first API call:

```
POST http://127.0.0.1:5000/api/detect-text
{ "text": "Artificial intelligence has fundamentally transformed ..." }
```

---

## Scene 4 — The server detects AI sentences

1. `backend/app.py` receives the call in the function `api_detect_raw_text()`. It passes the text on to `detect_text_service()` in `backend/aidetector/service.py`.
2. `clean_text()` (`backend/aidetector/pipeline/text_cleaner.py`) tidies extra spaces and punctuation.
3. `detect_text()` (`backend/aidetector/pipeline/detector.py`) does the main work:
   - `_load_model()` loads the detector. This happens only the first time, so the first detection is slower.
   - `_split_sentences()` cuts the text into sentences. It leaves out sentences shorter than 6 words, lines that look like citations (`[15] ...`), and captions that start with "Figure" or "Table".
   - `_group_into_paragraphs()` puts the sentences in groups of four. We call each group a **block**.
   - `_run_inference()` gives each block a score from 0 to 1.
   - Every sentence gets the score of its block. A score of 0.75 or more means the sentence is labelled `"ai"`. Anything lower is `"human"`.
4. `detect_text_service()` adds a summary (counts and the average score) and sends everything back.

**What comes back** (shortened):

```json
{ "sentences": [
    { "text": "Artificial intelligence has fundamentally ...", "label": "ai",    "score": 1.0 },
    { "text": "It is important to note that ...",              "label": "ai",    "score": 1.0 },
    { "text": "Furthermore, the integration of ...",           "label": "ai",    "score": 1.0 },
    { "text": "Moreover, it is crucial to consider ...",       "label": "ai",    "score": 1.0 },
    { "text": "My cat knocked a glass off the table ...",      "label": "human", "score": 0.0001 },
    { "text": "We went to the lake after lunch ...",           "label": "human", "score": 0.0001 } ],
  "summary": { "total_sentences": 6, "ai_sentences": 4, "score": 67 } }
```

Notice that sentences 1 to 4 share one score (they are one block), and sentences 5 and 6 share another.

---

## Scene 5 — The page shows the result

Back in `start()` (`Studio.tsx`), the function `load()` builds the page's list of sentences. Each sentence gets a record with:
- its text, plus a copy of the original text (used later by Undo),
- its label and score, plus a copy of the original score,
- a status, which starts as `idle`.

`load()` also keeps the score of each block and the overall score (67).

**You see**
- A summary card: **AI score at detection 67%** and **AI score now 67%**.
- The **View** switch: **Highlight** and **Compare** (Compare is greyed out for now).
- Your text. The four AI sentences are red and clickable. The two human sentences are plain.

**Files:** `ScoreSummary.tsx`, `ViewToggle.tsx`, `SentenceView.tsx`.

---

## Scene 6 — You click a red sentence

You click sentence 2, "It is important to note that ...".

**What happens in the page**
1. `SentenceView.tsx` calls `onHumanize(id)` in `Studio.tsx`.
2. The sentence turns blue and pulses, with a timer: "humanizing… 3s". After 15 seconds it adds "this can take a few minutes".
3. The page sends the second API call. It includes the sentence before and the sentence after, so the rewrite fits in. Those two are only background information. They are never changed.

```
POST http://127.0.0.1:5000/api/humanize-sentence
{ "text": "It is important to note that these technologies offer numerous benefits ...",
  "style": "academic",
  "context_before": "Artificial intelligence has fundamentally transformed ...",
  "context_after":  "Furthermore, the integration of machine learning ..." }
```

---

## Scene 7 — The server rewrites the sentence

This is the main part of the project.

1. `api_humanize_single_sentence()` in `app.py` receives the call. It hands it to `humanize_sentence_service()` in `service.py`.
2. The service checks the text is not empty. If the style is not one of the six, it uses "academic". It gets the humanizer (`get_humanizer()` creates it once and reuses it) and calls `humanize_single_sentence_smart()` in `backend/aidetector/pipeline/humanizer.py`.

**What `humanize_single_sentence_smart()` does**

1. It scores the original sentence alone. Say it gets 0.9999 (looks very AI).
2. It remembers a "best so far". At the start, the best is the original sentence.
3. **Humarin** tries first. It writes 5 versions. The detector scores each one. If a version scores lower than the best so far, it becomes the new best.
4. It looks at the best score. If it is **under 0.40**, that is good enough and it stops. If it is **0.40 or more**, it carries on.
5. **T5** tries next. It writes up to 3 versions. They are scored the same way.
6. **Gemini** tries next, if the best is still 0.40 or more. Gemini is Google's AI and runs over the internet. It is given the style, the sentence before and the sentence after, and it writes 3 versions. If the best is still 0.35 or more, it is asked for 3 simpler ones.
7. The **rule-based** rewriter is the last resort. It is plain code that swaps words and splits long sentences. It runs only if nothing has helped yet, or if the best is still 0.50 or more.
8. The winner is cleaned up: fancy words are swapped for simple ones, spacing is fixed, the sentence starts with a capital letter and ends with a full stop.
9. The server returns the best sentence, the score before and after, and the name of the winner.

If one rewriter fails, for example Gemini is not available, the code simply moves on to the next one.

| Rewriter | Where it runs | Versions it writes | When it runs |
|---|---|---|---|
| Humarin | your computer | 5 | always, first |
| T5 | your computer | up to 3 | best score still 0.40 or more |
| Gemini | Google, over the internet | 3 (then 3 more if needed) | best score still 0.40 or more |
| Rule-based | your computer | 1 | nothing helped yet, or best score 0.50 or more |

**What comes back** (a real example, T5 won):

```json
{ "humanized": "These technologies offer numerous benefits both for students and educators.",
  "original_score": 0.9999,
  "new_score": 0.7703,
  "engine": "t5" }
```
(The server also sends `improvement` and `processing_time`, and repeats these fields inside a `data` object.)

On this laptop one click takes about 12 seconds if Gemini is not used. A slow Gemini call can add minutes.

---

## Scene 8 — The page updates the sentence

When the answer arrives, `onHumanize()` in `Studio.tsx` decides what to show:

| What the server said | Sentence status | Colour |
|---|---|---|
| Rewritten and new score **below 0.40** | `humanized` | green |
| Rewritten but new score **0.40 or more** | `attempted` | amber |
| Winner is "original", or the text did not change | `unchanged` | grey, "No better rewrite" |
| The request failed | `error` | red message, click again to retry |

For our example the new score is 0.77, so the sentence turns **amber**. Its text is replaced with the new text. A badge shows the winner and the score ("Tier 2 · T5 · 0.77"), and an **↺ undo** link appears.

The badge score belongs to that one sentence.

---

## Scene 9 — The page checks the group score again

The numbers at the top are scores of blocks (groups of four), so the page needs a new score for the block that just changed.

1. A watcher in `Studio.tsx` notices that one block's text has changed.
2. It joins the four sentences of that block with spaces and sends the third API call:

```
POST http://127.0.0.1:5000/api/detector-score
{ "text": "<the four sentences of the block, joined>" }
```

3. On the server: `api_detector_score()` → `score_single_text_service()` → `score_single_text()` runs the detector once on that text.
4. The answer is a score, for example `{ "score": 0.9999 }`.
5. The page saves it and works out **AI score now** again. It is the average of all block scores.

A block changes slowly. In our tests, one rewritten sentence moved a block from 1.0 to 0.9999. Two rewritten sentences moved it to 0.1654.

---

## Scene 10 — You click another sentence

Scenes 6 to 9 happen again. For example, Gemini rewrites sentence 4. The new score is about 0.00, so it turns **green** with the badge "Tier 3 · Gemini · 0.00". The block is checked again and **AI score now** drops.

---

## Scene 11 — You click Compare

**Compare** becomes available after at least one sentence has been rewritten. Clicking it shows `CompareView.tsx` in place of the highlighted text:
- The left column has the original sentences. The right column has the new ones, row by row.
- Rewritten sentences are green or amber with their badge.
- A checkbox, **Show only changed sentences**, hides the rest.

No call to the server is made. It only reads what the page already has in memory.

---

## Scene 12 — You click Undo

1. `onUndo()` in `Studio.tsx` puts back the original text and the original score. The status goes back to `idle`.
2. The block text changed again, so Scene 9 repeats: the page asks for a new block score.
3. If no sentence is rewritten any more, the page switches back to the Highlight view.

---

## Scene 13 — You click Detect AI again

Everything is reset. Any reply still on its way from the earlier request is ignored.

---

## The same journey with a file upload

**You** click the upload box (or drag a file onto it) in the **Upload file** tab. `pickFile()` in `InputCard.tsx` accepts only `.pdf`, `.docx`, `.doc` and `.txt`.

1. You click **Detect AI**. `onUploadFile(file)` in `Studio.tsx` starts. The button says "Uploading…".
2. The page sends the file:
   `POST /api/detect` (the file is sent as a form upload).
3. The server (`create_detection_job()` in `service.py`) saves the file as `backend/uploads/aidetector_uploads/<job id>_<file name>`. It creates a **job** with a unique id and starts the work in the background. It answers at once: `{ "job_id": "...", "status": "processing" }`.
4. The button now says "Processing document…". Every 1.5 seconds the page asks:
   `GET /api/status/<job id>` — and gets `processing`, `done` or `error`.
5. Meanwhile the background work (`_process_file_background()` in `service.py`) runs:
   - `extract_text()` reads the file (PDF, Word or text) — `pipeline/pdf_extractor.py`.
   - `clean_extracted_text()` removes the References section, joins words that were split at the end of a line (keeping the hyphen), and drops page numbers.
   - `clean_text()` tidies the text.
   - Only the first **20,000 words** are kept.
   - `detect_text()` scores it, exactly as in Scene 4.
6. When the status is `done`, the page asks for the result:
   `GET /api/result/<job id>` — the same sentences and summary as in Scene 4.
7. The page then asks the server to delete the job and the saved file:
   `DELETE /api/status/<job id>`.
8. From here it is Scene 5 onwards. If the document had 20,000 words or more, an amber banner says only the first 20,000 words were analysed.

If the file has no readable text, for example a scanned PDF, the job ends with an error and the page shows the message in red.

---

## When something goes wrong

| What happens | What you see |
|---|---|
| The backend is not running | Red message: "Cannot reach the backend … Is it running?" |
| Gemini is down or out of quota | The sentence is still rewritten by another rewriter; the winner badge shows which |
| No rewriter can improve the sentence | Grey badge "No better rewrite" |
| The group-score check fails | Amber note under the summary: the "now" score may be out of date |
| You start a new detection while a rewrite is running | The old reply is ignored |

---

## Where to find things

| You want to see… | Open |
|---|---|
| The page and all its memory | `frontend/src/components/Studio.tsx` |
| The messages sent to the server | `frontend/src/lib/api.ts` |
| The input card, upload and drag-and-drop | `frontend/src/components/InputCard.tsx` |
| Red/green/amber sentences | `frontend/src/components/SentenceView.tsx` |
| Side-by-side view | `frontend/src/components/CompareView.tsx` |
| The server's addresses | `backend/app.py` |
| What each address does | `backend/aidetector/service.py` |
| Cutting into sentences and scoring | `backend/aidetector/pipeline/detector.py` |
| The four rewriters | `backend/aidetector/pipeline/humanizer.py` and `t5_humanizer.py` |
| Reading uploaded files | `backend/aidetector/pipeline/pdf_extractor.py` |
| Settings (API key, model name) | `backend/.env` |
