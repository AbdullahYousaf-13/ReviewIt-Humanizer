# Diverse beam search: results (Humarin and T5)

Date: 2026-10-19. The experiment code, test scripts and raw results were never merged into this branch. They are archived under the git tag `archive/humarin-diverse-beams` (the branch itself was deleted). To look at them: `git checkout archive/humarin-diverse-beams`.

*Historical note (26 Oct): these are the results of 19 Oct, before the guard and the citation routing existed. "Passing" here means a score below 0.40 plus the quality gate of that experiment, not the current guard. Diverse beams were not adopted (only T5's 3 beams were).*

**Problem:** Humarin's 5 candidates are near-identical, so if one is flagged all are, and most sentences fall to the fallbacks. The T5 fallback has the same problem.
**Change tested:** diverse beam search (each beam in its own group, diversity penalty 4) instead of plain beam search. Off by default, enabled with `HUMARIN_DIVERSE_BEAMS=1` (covers Humarin and T5). `T5_NUM_BEAMS` and `T5_DIVERSITY_PENALTY` set T5 separately.

## Tests
1. **Humarin benchmark:** 52 AI-written sentences, several penalty values, scored with our BERT detector (28 of them are flagged by BERT).
2. **T5 benchmark:** the 28 flagged sentences, current T5 vs diverse beams with 3, 4 and 5 beams (penalty 4).
3. **Real paper:** 20 real flagged sentences from a published paper, run through the real click-to-humanize pipeline (Humarin, then T5, then rule-based; Gemini off). Current = `abdullah/humanizer-dev`.

All tables use the same columns. **AI score average:** average final BERT score (lower is better). **Passing:** sentences scoring below 0.40 (in tests 1 and 2, also keeping all numbers and citations and passing the quality gate). **Meaning kept:** of the passing sentences, how many kept their meaning, judged by reading the outputs (small sample).

## Results

**Test 1, Humarin (28 flagged, 5 beams, penalty varied):**

| Setting | AI score average | Passing | Meaning kept | Time per sentence |
|---|---|---|---|---|
| Current (plain beam) | 0.96 | 1 / 28 | not read | 3.6 s |
| Penalty 2 | 0.81 | 5 / 28 | 4 of 5 | 3.9 s |
| Penalty 3 | 0.75 | 7 / 28 | ~6 of 7 | 4.0 s |
| **Penalty 4** | **0.56** | **13 / 28** | **~9-10 of 13** | 4.0 s |
| Penalty 5 | 0.58 | 12 / 28 | ~9 of 12 | 4.0 s |
| Penalty 12 and 20 (identical) | 0.48 | 15 / 28 | ~7 of 15 | 4.2 s |

Penalties above 5 add more passing sentences but also more garbled ones, so 4-5 is the sweet spot.

**Test 2, T5 (28 flagged, penalty 4, beams varied):**

| Setting | AI score average | Passing | Meaning kept | Time per sentence |
|---|---|---|---|---|
| Current (4 beams, plain) | 0.79 | 7 / 28 | 7 of 7 (6 are comma-only edits) | 7.1 s |
| Diverse, 3 beams | 0.71 | 9 / 28 | 8 of 9 | 7.0 s |
| **Diverse, 4 beams** | **0.62** | **12 / 28** | **~10 of 12** | 7.6 s |
| Diverse, 5 beams | 0.56 | 13 / 28 | ~8 of 13 | 8.5 s |

4 beams is the best balance. 5 beams leaked a German word ("Insgesamt") and garbled some outputs.

**Test 3, real paper (20 sentences).** Run A and run B were on different machine load, so compare each new row with the current row from the same run.

| Setting | AI score average | Passing | Meaning kept | Time per sentence |
|---|---|---|---|---|
| Current (run A) | 0.61 | 8 / 20 | 16 of 20 | 5.4 s |
| Humarin diverse, penalty 4 (run A) | **0.47** | **11 / 20** | ~14 of 20 | 5.0 s |
| Current (run B) | 0.61 | 8 / 20 | 16 of 20 | 9.7 s |
| Humarin + T5 diverse (run B) | **0.47** | **11 / 20** | ~14 of 20 | 9.4 s |

For test 3, meaning kept is counted over all 20 final outputs (unchanged sentences count as kept).

## Verdict
- **Humarin diverse (penalty 4): keep.** +3 passing sentences on the real paper, a large gain in the benchmark, same speed. Meaning is slightly worse because the lowest-scoring candidate is not always the most faithful.
- **T5 diverse: not proven in the pipeline.** It helps in the benchmark, but on the real paper it gained one sentence and lost one, because T5 only sees the sentences Humarin already failed on, and diverse beams can drop the normal best candidate.
- **Next:** try 2 groups of 2 beams instead of 5 groups of 1, add the plain top candidate to the diverse set, and reject stray `''` and non-English words. Also reject bracketed text not in the original (e.g. "[citation needed]"), and keep the original sentence when the final score is still >= 0.40 (see B18 in `OPEN_ISSUES.md`).
