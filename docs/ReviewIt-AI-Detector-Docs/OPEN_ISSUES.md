# Open Issues

Last updated 2026-10-29 (branch `abdullah/humanizer-new-engine`). **Only issues that are still open are listed**; fixed ones are in `FIXED_ISSUES.md`. Old B3 (insecure defaults) and B9 (styles had little effect) were fixed on 27 Oct and moved there. Items come from the original backend unless marked *new*.

## Backend

| # | Issue | Detail |
|---|---|---|
| B4 | Layout rules are heuristics with known gaps | Unchanged: run-in headings in the same style, figures without shapes, multi-column papers untested, text boxes, equation-heavy papers, English-only captions, short list items shown as headings. Scanned PDFs are not supported by decision. |
| B8 | *new* — General abstract sentences stay high when scored alone (lists are mostly fixed) | Since 28 Oct the prompt turns any run of three or more items into clauses with verbs or splits it unevenly, and the retry says the same. In the 29 Oct full-paper run every list and definition sentence scored 18% or below alone and the document went from 24 red sentences to 4 (mean 3%). Still high alone: sentences made of abstract nouns, such as "Researchers and educators need to understand the potential, opportunities and challenges…" (#136, 99–100%), #27 (100%) and #117 (74–97%). They sit inside low-scoring blocks, so they are not red in the document. No reliable prompt fix is known. |
| B12 | *new* — A click takes 10–35 s on this PC | In the 29 Oct "Humanize all" run (26 sentences, one after the other) a click took 4–35 s, mean 12.7 s. Uncited sentences took 10–35 s because Humarin (5–16 s) and T5 (3–22 s) run next to Gemini (3–10 s) and set the total; cited sentences (Gemini only) took 6–10 s. The whole run took about 5 min 50 s. **Decision (2026-10-27): leave Humarin as is.** |
| B13 | *new* — Gemini prices change on 2027-01-01 | The cost log uses $0.75 / $3.75 per 1M tokens (paid tier until 31 Dec 2026); from 1 Jan 2027 it is $1.50 / $7.50. Update `GEMINI_PRICE_INPUT_PER_M` / `GEMINI_PRICE_OUTPUT_PER_M`. |

## Frontend

| # | Issue | Detail |
|---|---|---|
| F2 | Things noticed in the colleague's frontend | Still open: (4) the Humanizer studio page shows a fixed latency and counts sentences with its own regular expression; (5) no request queue: the server handles one humanize request at a time; (6) no message when a document was cut to 20,000 words (the API has no flag for it, and the contract is locked); (8) History, Settings, the credit counter and the Plagiarism page use local or sample data. Partly open: (1) the overall score averages single-sentence scores while the detector scores blocks of 4; since 29 Oct a humanized sentence counts at no more than the par score (30%) in that average, untouched sentences count at their own score. Fixed since 22 Oct: (2) a failed rewrite is no longer marked as rewritten; (3) "Humanize all" and Compare use the selected style; (7) `GET /styles` exists in the backend. Changed on 29 Oct on our branch: the per-sentence AI percentages and the Advanced / Standard tags are removed; the Flagged / Mixed / Human counts and filters treat a humanized sentence as human (it is shown green); the "Highlight" tab is called "View". |
