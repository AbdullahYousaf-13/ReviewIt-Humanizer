# Open Issues

Last updated 2026-10-27 (branch `abdullah/humanizer-new-engine`). **Only issues that are still open are listed**; fixed ones are in `FIXED_ISSUES.md`. Old B3 (insecure defaults) and B9 (styles had little effect) were fixed on 27 Oct and moved there. Items come from the original backend unless marked *new*.

## Backend

| # | Issue | Detail |
|---|---|---|
| B1 | Whole-document humanize deferred | `/api/humanize` is out of scope (focus: click-to-humanize). The frontend's "Humanize all" calls `/api/humanize-sentence` once per flagged sentence, with the selected style, so no new endpoint is needed. |
| B2 | Three API implementations | The frontend uses Flask `app.py`. `aidetector/main.py` (FastAPI) re-implements the endpoints with its own logic; `aidetector/api/main.py` cannot start (`ImportError`). **Decision (2026-10-21, supervisor): leave as is.** |
| B3 | API routes mostly untested; the paid Gemini path is tested only by hand | 278 tests (`backend/tests`, `python -m pytest tests -q`) cover the pipeline, guard, prompt, Word files, styles, server defaults (CORS, upload limit) and the humanize service. Most Flask routes are not tested directly. The real Gemini output was checked in two paid runs (67 and 36 calls, see `GEMINI_PIPELINE_TEST_2026-10-27.md` and `GEMINI_PROMPT_V2_TEST_2026-10-27.md`); the tests use fake Gemini replies. |
| B4 | Layout rules are heuristics with known gaps | Unchanged: run-in headings in the same style, figures without shapes, multi-column papers untested, text boxes, equation-heavy papers, English-only captions, short list items shown as headings. Scanned PDFs are not supported by decision. |
| B5 | The detector reads citations as a sign of human text | Unchanged. **Decision (2026-10-21): keep citations in the scored text.** To confirm with the supervisor which detector the tool is meant to beat. |
| B6 | Direct quotations are not protected | Unchanged. Planned: reject a rewrite that does not contain every double-quoted passage of 4+ words word for word. Not built. |
| B7 | A score that barely improves still counts | A rewrite going 1.0000 → 0.9998 is kept and shown as 100%. **Decision (2026-10-27): leave as is.** |
| B8 | *new* — List and definition sentences stay flagged | In both paid runs, sentences that are lists or definitions ("Examples of AI tools used in education are …", "AI tools are software programs that …") scored 100% in all rewrites, even with the stronger restructuring rule. Detectors flag predictable wording, and these sentences are predictable by nature. No reliable prompt fix is known. |
| B9 | *new* — Small meaning changes are not caught automatically | The prompt's meaning rules reduce them, but the paid run still showed a softened phrase ("must find ways" → "are sought"), a dropped phrase and one added word. The guard checks numbers, citations, negation, direction, length and endings, not meaning. **Decision (2026-10-27): no meaning-checker model.** |
| B10 | *new* — Old .doc files are not supported | **Decision (2026-10-27, supervisor): leave .doc out.** A `.doc` upload is refused with "save it as .docx or PDF"; an old Word file renamed to `.docx` gets the same kind of message. The frontend's file picker still offers `.doc` (colleague's code, not changed). |
| B11 | *new* — Removing a sentence changes its neighbours' scores | The detector scores blocks of 4 sentences, so dropping a sentence (for example the new back-matter skip) regroups the blocks after it. On the test paper: 24 flagged + 3 mixed became 26 flagged + 0 mixed. Expected from the block design, not a bug. |
| B12 | *new* — A click takes 9–19 s on this PC | Academic sentences without a citation run Gemini, Humarin and T5 every click (Humarin is the slow part on the CPU; Gemini is about 3–4 s). **Decision (2026-10-27): leave Humarin as is.** |
| B13 | *new* — Gemini prices change on 2027-01-01 | The cost log uses $0.75 / $3.75 per 1M tokens (paid tier until 31 Dec 2026); from 1 Jan 2027 it is $1.50 / $7.50. Update `GEMINI_PRICE_INPUT_PER_M` / `GEMINI_PRICE_OUTPUT_PER_M`. |

## Frontend

| # | Issue | Detail |
|---|---|---|
| F1 | Whole-document humanize in one request is not available | Deferred on purpose (see B1). |
| F2 | Things noticed in the colleague's frontend | Still open: (1) the overall score averages single-sentence scores while the detector scores blocks of 4; (4) the Humanizer studio page shows a fixed latency and its own sentence count; (5) no queue: the server handles one humanize request at a time; (6) no message when a document was cut to 20,000 words; (8) History, Settings, the credit counter and the Plagiarism page use local or sample data. Fixed since 22 Oct: (2) a failed rewrite is no longer marked as rewritten; (3) "Humanize all" and Compare use the selected style; (7) `GET /styles` exists in the backend. |
