# AI Detector & Humanizer: API Flow (FE -> BE)

Base URL: `http://127.0.0.1:5000` (frontend: `frontend/lib/api.ts`). Backend routes: `backend/app.py`.

## Flow

```
PASTE TEXT
FE ── POST /api/detect-text ──────────► BE
FE ◄─ sentences + scores ─────────────  BE

UPLOAD FILE
FE ── POST /api/detect (file) ────────► BE
FE ◄─ job_id ─────────────────────────  BE
FE ── GET  /api/status/{jobId} ───────► BE   (repeat until done)
FE ── GET  /api/result/{jobId} ───────► BE
FE ◄─ sentences + scores ─────────────  BE
FE ── DELETE /api/status/{jobId} ─────► BE   (cleanup)

HUMANIZE A SENTENCE
FE ── POST /api/humanize-sentence ────► BE
FE ◄─ humanized text + new score ─────  BE
```

## Where each call is written

| Call | Frontend | Backend |
|---|---|---|
| `POST /api/detect-text` | `frontend/lib/api.ts` | `backend/app.py` |
| `POST /api/detect` | `frontend/lib/api.ts` | `backend/app.py` |
| `GET /api/status/{jobId}` | `frontend/lib/api.ts` | `backend/app.py` |
| `GET /api/result/{jobId}` | `frontend/lib/api.ts` | `backend/app.py` |
| `DELETE /api/status/{jobId}` | `frontend/lib/api.ts` | `backend/app.py` |
| `POST /api/humanize-sentence` | `frontend/lib/api.ts` | `backend/app.py` |

## JSON responses

### POST /api/detect-text
Request: `{"text": "..."}`
```json
{
  "success": true,
  "score": 0.4213,
  "score_pct": 42,
  "label": "ai",
  "sentences": [
    {"text": "First sentence.", "label": "ai", "score": 0.9132, "para": 0},
    {"text": "Second sentence.", "label": "human", "score": 0.1204, "para": 0}
  ],
  "headings": [{"text": "Introduction", "para": 0}],
  "summary": {
    "total_sentences": 2, "ai_sentences": 1, "human_sentences": 1,
    "average_score": 0.4213, "score": 42,
    "total_words": 5, "total_characters": 34
  }
}
```
`label` is `"ai"` when `score_pct` is 30 or more (the par score; it was 40 until 2026-10-28). Empty text returns `{"error": "Text cannot be empty"}` (HTTP 400).

### POST /api/detect
Request: file in form field `file` (pdf, docx, txt; an old `.doc` file is rejected with a plain message).
```json
{"job_id": "<uuid>", "status": "processing", "filename": "x.pdf"}
```

### GET /api/status/{jobId}
```json
{
  "job_id": "<uuid>", "status": "processing", "filename": "x.pdf",
  "elapsed_seconds": 3.42, "error": null, "error_code": null
}
```
`status` is `processing`, `done` or `error`.

### GET /api/result/{jobId}
When done:
```json
{
  "status": "done",
  "sentences": [{"text": "...", "label": "ai", "score": 0.9132, "para": 0}],
  "headings": [{"text": "...", "para": 0}],
  "notes": [],
  "humanized_full": "",
  "summary": {
    "total_sentences": 0, "ai_sentences": 0, "human_sentences": 0,
    "average_score": 0.0, "score": 0,
    "total_words": 0, "total_characters": 0, "preview": "..."
  },
  "filename": "x.pdf"
}
```
While processing: `{"status": "processing", "sentences": [], "headings": [], "humanized_full": "", "summary": {}, "filename": "x.pdf"}`.
On failure: same shape with `"status": "error"`, plus `"error"` and `"error_code"`.

### DELETE /api/status/{jobId}
```json
{"status": "deleted", "job_id": "<uuid>"}
```

### POST /api/humanize-sentence
Request: `{"text", "style", "context", "context_before", "context_after", "original_score"}` — `original_score` is **optional** (added 2026-10-28): the score the first scan gave the sentence, a number from 0 to 1 (for example `0.97`). When it is sent the backend uses it as the original's score and does **not** score the original again; anything else (missing, text, true/false, negative, above 1, `97`) is ignored and the backend scores the original itself, as before. The response keys do not change; the response `original_score` is then the number that was sent, and `improvement`, `failed` / `reason` and which rewrites are shown are calculated from it (when no rewrite beats it, `engine` is `"original"`, `failed` is `true` and `new_score` equals it).
Styles: `academic` (default), `business`, `creative`, `casual`, `narrative`, `technical`. An unsupported style returns HTTP 400.
```json
{
  "success": true,
  "data": {
    "original": "...",
    "humanized": "...",
    "original_score": 0.93,
    "new_score": 0.21,
    "improvement": 0.72,
    "engine": "humarin",
    "failed": false,
    "reason": "",
    "alternatives": [
      {"engine": "humarin", "humanized": "...", "new_score": 0.18, "improvement": 0.75},
      {"engine": "t5", "humanized": "...", "new_score": 0.35, "improvement": 0.58}
    ]
  },
  "processing_time": 4.812,
  "humanized": "...",
  "new_score": 0.21,
  "original_score": 0.93,
  "improvement": 0.72,
  "engine": "gemini",
  "alternatives": [
    {"engine": "humarin", "humanized": "...", "new_score": 0.18, "improvement": 0.75},
    {"engine": "t5", "humanized": "...", "new_score": 0.35, "improvement": 0.58}
  ]
}
```
`engine` is one of `humarin`, `t5`, `gemini`, `rule_based`, `original`. `original` means no safe rewrite was found at all (see the last resort below), and `failed` is then `true` with a `reason`.

**`alternatives` (added 2026-10-26, additive: no existing key changed).** Every click runs Gemini, Humarin and T5. The main result (`humanized`, `engine`, `new_score`, ...) is Gemini's whenever it passes the fact guard and scores below the original; otherwise it is the lowest-scoring of the other two. `alternatives` lists the other rewrites that also passed the guard and scored below the original, in this order: **Gemini's second-best rewrite** (`engine: "gemini"`, added 2026-10-27 — the page shows Gemini's two best rewrites), then `humarin`, then `t5` (at most one entry each). The key and the entry fields did not change; only a second `"gemini"` value can now appear. It is `[]` when there are none (also when `failed` is `true`). `rule_based` runs only when nothing else is good enough, and never appears in `alternatives`. Each entry has `engine`, `humanized`, `new_score`, `improvement`. Present both inside `data` and at the top level.

**Which rewrites are shown, and in what order (2026-10-28, values only: no key changed).** The par score is **30%** (it was 40%): a score below it counts as human. Gemini's first call asks for 5 rewrites and its retry for 2 (changed 2026-10-29).
- Gemini's best rewrite is shown whenever it beats the original, even above 30%; its second rewrite only at 30% or below.
- Humarin's, T5's and the rule-based engine's rewrites are shown only at 30% or below (and below the original); the rule-based engine is a local engine like the other two (never "Recommended" by default).
- If none of Gemini's rewrites is at 30% or below, Gemini is called once more (one retry, at most two calls per click) and the results of both calls compete.
- **Last resort (2026-10-29):** if no engine has a rewrite that beats the original but Gemini has a safe one, Gemini's best rewrite is shown anyway (even at 100%), as `humanized` with `engine: "gemini"`, `failed: false` and `improvement: 0`. The original comes back (`engine: "original"`, `failed: true`) only when Gemini has no safe rewrite at all.
- Order: Gemini's rewrites first while one of them is at 30% or below, then Humarin / T5 (lower score first). If none of Gemini's is at 30% or below but a Humarin / T5 one is, **that one is first** (it becomes `humanized` / `engine`) and Gemini's best follows it. So `engine` of the main result can be `humarin` or `t5` even when Gemini answered, and `alternatives` is in display order.
- The page names them by rank, not by engine: the first is "Recommended", the others "Option 1", "Option 2", "Option 3".
- `label` of `/api/detect-text` is `"ai"` from `score_pct` 30 (it was 40).

**Styles and citations (2026-10-26):** only Gemini applies a style and only Gemini keeps a citation reliably, so Humarin, T5 and the rule-based engine run for the default style (`academic`) and a sentence **without** a citation only; a sentence with a citation always goes to Gemini alone (`alternatives` is `[]`, and if Gemini gives nothing usable it comes back unchanged with `failed: true` and a reason that does not name a model). For any other style only Gemini runs, so `alternatives` can only hold Gemini's second rewrite. The page shows the rewrites as "Recommended" (the main result) and "Option 1", "Option 2"…; `engine` and the scores are not shown to users.

Note: these JSON bodies are the shapes the code produces ([service.py](backend/aidetector/service.py)), not captured from a live run.
