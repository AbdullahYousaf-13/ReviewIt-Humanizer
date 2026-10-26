# AI Detector & Humanizer: API Flow (FE -> BE)

Base URL: `http://127.0.0.1:5000` (frontend: [api.ts:10](frontend/src/lib/api.ts#L10)). Backend routes: [app.py](backend/app.py).

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
| `POST /api/detect-text` | [api.ts:68](frontend/src/lib/api.ts#L68) | [app.py:69](backend/app.py#L69) |
| `POST /api/detect` | [api.ts:74](frontend/src/lib/api.ts#L74) | [app.py:57](backend/app.py#L57) |
| `GET /api/status/{jobId}` | [api.ts:78](frontend/src/lib/api.ts#L78) | [app.py:174](backend/app.py#L174) |
| `GET /api/result/{jobId}` | [api.ts:81](frontend/src/lib/api.ts#L81) | [app.py:186](backend/app.py#L186) |
| `DELETE /api/status/{jobId}` | [api.ts:85](frontend/src/lib/api.ts#L85) | [app.py:174](backend/app.py#L174) |
| `POST /api/humanize-sentence` | [api.ts:113](frontend/src/lib/api.ts#L113) | [app.py:79](backend/app.py#L79) |

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
`label` is `"ai"` when `score_pct` is 40 or more. Empty text returns `{"error": "Text cannot be empty"}` (HTTP 400).

### POST /api/detect
Request: file in form field `file` (pdf, docx, doc, txt).
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
Request: `{"text", "style", "context", "context_before", "context_after"}`
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
`engine` is one of `humarin`, `t5`, `gemini`, `rule_based`, `original`. `original` means no rewrite beat the original, and `failed` is then `true` with a `reason`.

**`alternatives` (added 2026-10-26, additive: no existing key changed).** Every click runs Gemini, Humarin and T5. The main result (`humanized`, `engine`, `new_score`, ...) is Gemini's whenever it passes the fact guard and scores below the original; otherwise it is the lowest-scoring of the other two. `alternatives` lists the other engines that also passed the guard and scored below the original: at most one entry each, in the order `humarin`, `t5`. It is `[]` when there are none (also when `failed` is `true`). `rule_based` runs only when nothing else is good enough, and never appears in `alternatives`. Each entry has `engine`, `humanized`, `new_score`, `improvement`. Present both inside `data` and at the top level.

**Styles and citations (2026-10-26):** only Gemini applies a style and only Gemini keeps a citation reliably, so Humarin, T5 and the rule-based engine run for the default style (`academic`) and a sentence **without** a citation only; a sentence with a citation always goes to Gemini alone (`alternatives` is `[]`, and if Gemini gives nothing usable it comes back unchanged with `failed: true` and a reason that does not name a model). For any other style `alternatives` is also always `[]`. The page shows the rewrites as "Recommended" (the main result), "Option 2" and "Option 3"; `engine` is not shown to users.

Note: these JSON bodies are the shapes the code produces ([service.py](backend/aidetector/service.py)), not captured from a live run.
