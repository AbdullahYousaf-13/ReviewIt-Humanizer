# Retry and first call: experiments and live runs, 2026-11-02

Why this was done: in the run that first logged scores (22 clicks), only 12 of 22 humanized sentences really reached the par score (30% or below); the other 10 were shown as human although they stayed at 93–100% (one at 38%), and only 1 of 11 retries rescued its sentence. The question was which change to the prompt would fix that, and what the evidence says about it.

**Short version**
- Ordinary-length rewrites almost never pass (1 of 31 candidates); rewrites that say the same thing in more words (1.5–2 times the length) pass much more often (20 of 83). Structure-only changes (split, active/passive, start elsewhere, verb clauses) did not help at all offline (0 of 20).
- Whether a sentence passes depends more on the sentence than on the prompt: some sentences passed 5 of 6 times, others 0 of 16.
- Live results differ a lot from run to run (the same 8 sentences gave 8 of 8 and 5 of 8), so no single run proves a change.
- A final "too" brought 5 of 5 failing rewrites below 30% offline, but a code step built on it did nothing on the live Kumasi sentence (12 variants, all 100%) and was removed on 2 Nov.
- Spelled-out rewrites can drift in meaning (2 of 5 checked); the prompt asks against it, the guard cannot see it.

What was built from this (ReviewIt, branch `abdullah/humanizer-new-engine`): `243696f` retry and `37511ca` first call; two local-only `log:` commits for the diagnostic log. Details: `CODE_FLOW.md` Scene 6, `FIXED_ISSUES.md` FB59–FB64, `OPEN_ISSUES.md` B4–B8. Later that day: a prompt line against "without", a guard rule and the closest-length ranking (FB62–FB64).

---

## 1. The 16 sentences

The first 16 AI-flagged sentences of one paper (nursing leadership succession, 851 sentences, 751 flagged, `gemini-3.8-flash`, Academic style). All start at a block score of 100%. Numbers are the order in which they were clicked.

1. Nursing leadership succession planning is vital for maintaining organizational resilience and high-quality patient care.
2. Within sub-Saharan Africa, and Ghana in particular, the structural implementation of succession management systems remains constrained by acute resource limitations and an escalating professional brain drain.
3. Guided by Organisational Learning Theory (OLT), this study explored nursing leadership succession planning practices and organizational preparedness across public, private, and faith-based healthcare facilities in Kumasi, Ghana. (the "Kumasi sentence")
4. A qualitative, multiple-case study design anchored in an interpretivist paradigm was employed.
5. Purposive sampling was used to recruit key stakeholders across three hospital ownership models in the Ashanti Region.
6. Data collection comprised semi-structured individual interviews (n = 18), focus group discussions (n = 3), and organizational document reviews.
7. Data were analyzed using reflexive thematic analysis.
8. The empirical results revealed that nursing leadership succession planning was predominantly informal, reactive, and vacancy-driven across all contexts.
9. Formal written succession policies and standardized transition pathways were entirely absent.
10. Despite this lack of structural infrastructure, organizations sustained leadership continuity through dynamic, informal organizational learning processes.
11. Emerging leaders were progressively prepared via experiential workplace learning, delegated responsibilities, acting appointments, and informal mentoring.
12. Document analysis revealed a distinct cross-case divergence: public and faith-based settings utilized standardized, written handover notes, whereas the private facility relied on brief, verbal orientations.
13. Crucially, existing transition mechanisms excelled at tracking physical and operational assets but systematically failed to capture the strategic, tacit, and relational insights necessary to navigate complex human and cultural dynamics.
14. While informal organizational learning processes maintain operational continuity, they leave health institutions vulnerable to sudden leadership disruption.
15. To maximize workforce sustainability, healthcare organizations must move away from reactive replacement planning.
16. Existing informal mechanisms must be systematically institutionalized within formal, policy-driven succession planning frameworks.

Scored alone, 15 of them are at 98–100%; sentence 4 scores only 9% alone (its "100%" is the block score).

---

## 2. Live runs

"Pass" = the shown rewrite is at 30% or below and below the original (`par=yes`). Runs 1–2 were before the score was logged, so the passes of retried clicks are unknown for run 1.

| Run | Code | Sentences | Passed | First call | Retries (rescued) | Cost |
|---|---|---|---|---|---|---|
| 1 | retry of 2 | 30 clicks (incl. the 16) | 11 proven (the rest unknown) | 11 | 19 (unknown) | about $0.084 |
| 2 | retry of 2, score logged | 22 | 12 of 22 | 11 | 11 (1) | $0.064 |
| 3 | retry of 5, old retry text | 16 | 11 of 16 | 8 | 8 (3) | $0.042 |
| 4 | new Academic retry text (`243696f`) | 16 | **15 of 16** | 10 | 6 (5) | $0.039 |
| 5 | + new first call, faithfulness rule, word range (`37511ca`) | 8 complete (9th cut off) | 5 of 8 | 3 | 5 (2) | $0.0265 |
| 6 | same code as 5 | 8 (sentence 1 missing, sentence 16 added) | 6 of 8 | 6 | 2 (0) | $0.0211 |
| 7 | same code | 1 (the Kumasi sentence, from the screen) | 0 of 1 | 0 | 1 (0) | $0.0051 |
| 8 | same code, **another paper** (digital-services trade, NLP in finance) | 10 (first and last click partly cut off) | **10 of 10** | 9 | 1 (1: 5 of 5 candidates passed) | about $0.0024 per sentence |

Notes
- **Run 4 against runs 5–6 on sentences 1–8:** 8 of 8, then 5 of 8, then 6 of 8 (with one sentence swapped). The failures moved: Kumasi failed in both later runs; succession planning and reflexive analysis failed in run 5 (succession planning was not clicked in run 6); data collection failed in run 6 only.
- **The first call is not stable:** sentences 8 and 14 failed their first call in runs 1 and 3 and passed it in run 4.
- **Run 4's retry rescued 5 of 6** (succession planning, Kumasi at 21%, purposive sampling, data collection, reflexive analysis); runs 5–6 rescued 2 of 7. The prompt changed between them (faithfulness rule, word range, a different first call), but one run each cannot separate that from variance.
- **Cost:** the longer first-call prompt costs about $0.0005 more per call (input 1,400 → 1,750 tokens); run 5–6 clicks cost $0.0026–0.0033 per sentence.

**A different paper (run 8, 15:51):** every click reached 30% or below. On its 9 fully logged clicks the spelled-out first-call rewrites passed 15 of 24 (3 more were rejected for an added negation) and the ordinary ones 5 of 18, against 14 of 48 and 1 of 31 on the nursing paper. The prompt works much better on these sentences; the sentences that stay above 30% are the nursing paper's. The same log showed the problems fixed later that day: a longer rewrite shown although a short faithful one also passed (4 of 10 clicks), shown winners that add content, "without …" rewrites thrown away, and a broken rule-based option.

### Per candidate, from the diagnostic log (runs 5–6, 16 clicks, 114 candidates)

| Candidates | At 30% or below |
|---|---|
| Ordinary first-call rewrites (1 and 2) | **1 of 31** (3%) |
| Spelled-out first-call rewrites (3–5) | **14 of 48** (29%) |
| Retry rewrites (all spelled out) | 6 of 35 (17%) |

- By shape (retry, 7 each): same order 1, two sentences 1, starts elsewhere 1, verb clauses 2, two sentences + verb clauses 1: no shape stands out. First call: same order 6 of 16, starts elsewhere 5 of 16, two sentences 3 of 16.
- By length ratio of the spelled-out candidates: 1.3–1.5× 3 of 5, 1.5–1.7× 7 of 26, 1.7–1.9× 8 of 42, 1.9–2.3× 2 of 10: no gain beyond 1.5×.
- In a third run (15:04) the Kumasi sentence again gave 10 rewrites, all at 100%.
- By sentence (all spelled-out candidates): "Existing informal mechanisms…" 3 of 3, sub-Saharan 5 of 6, interpretivist 5 of 11, empirical results 3 of 6, purposive 3 of 11, reflexive 1 of 11, succession planning 0 of 8, data collection 0 of 11, **Kumasi 0 of 16**.
- In 2 of 8 clicks in run 6 the spelled-out rewrites passed where both ordinary ones failed (sub-Saharan, empirical results): without them those clicks would have needed a retry.
- The "ordinary" rewrites are not always ordinary: in run 5, 6 of the 16 were longer than the 30% they were asked to stay within (up to 1.74×).

---

## 3. Offline experiments (the app's detector, no Gemini call)

Scores are the detector's score of the text alone, exactly as the pipeline scores a rewrite. Before use, the scoring was checked against the logged scores of five Gemini rewrites: identical to four decimals.

### E1. Structure or length? (`move_experiment.py`, `move_experiment_2.py`)
Five sentences that still scored 97–100% after 10 Gemini rewrites (succession planning, Kumasi, purposive sampling, emerging leaders, informal learning), 64 hand-written rewrites that keep the meaning and pass the fact guard.

| What | At 30% or below |
|---|---|
| Structure only: split in two, active/passive, start elsewhere, verb clauses | **0 of 20** (all 98.8% or more) |
| Plainer, wordier wording: alone / with a split / with start elsewhere / with verb clauses | 2 of 5 / 3 of 5 / 2 of 5 / 1 of 5 |
| Rewrites 1.5× the target's length or longer | **10 of 23** |
| Rewrites shorter than 1.5× | 6 of 41 |
| The formal wording padded to the same length ("by means of", "that was used in order to") | 2 of 5, so length matters, not only plainer words |
| The Kumasi sentence (names, acronym, list, place), any variant | **0 of 15** |

Putting the formal phrases back into a passing variant one at a time: for "Nursing leadership succession planning…" restoring "organizational resilience" or "succession planning for nursing leadership" killed the pass, restoring "high-quality patient care" did not.

### E2. Why "Emerging leaders…" resists (`s4_factorial.py`)
A list of four items. Each item kept or reworded, in a single sentence and in a two-sentence frame (32 variants): **0 of 32** reached 30%. The last words decided it: the same text ending "…also helped prepare them." 0 of 16, "…helped prepare them." 0 of 16, "…helped prepare them too." **6 of 16**, "…helped prepare them as well." 4 of 16. So this sentence's score depends on incidental surface details that a prompt cannot target.

### E3. Do passing rewrites keep fewer of the original's words? (`retention.py`)
27 full-text rewrites from runs 3–4. Passing rewrites (22) keep on average 0.75 of the original's content words, failing ones (5) 0.80. **No difference**, so "replace more words" is not a lever.


---

## 4. Faithfulness check of 5 retry rewrites (run 4)

| Sentence | Verdict | What |
|---|---|---|
| Succession planning | **Drift** | "Care … is vital" and "keeping an organization resilient" became separate claims; "current" was added |
| Kumasi | Faithful | all three facility types kept |
| Purposive sampling | Borderline | "Three hospital ownership models were represented in the Ashanti Region" is a new standalone statement |
| Data collection | Faithful | numbers kept |
| Reflexive analysis | Faithful | padded, no new claim |

A visible example in run 5: the winner "Purposive sampling was used when recruiting key stakeholders who work across three models of hospital…" says the stakeholders work across the models; the original says they were recruited across them (the lowest score won over a 1% rewrite).

---

## 5. What is not known

- Whether the first-call change (2 ordinary + 3 spelled out) beats the old first call: two runs, 3 of 8 and 6 of 8, against 2, 3 and 3 of 8 before.
- Whether the faithfulness rule or the word range lowered the retry's success (5 of 6 in run 4, 2 of 7 in runs 5–6), or whether that is variance.
- One paper, one detector (the local BERT model), one Gemini model.

## 6. Decisions taken
- Faithfulness is asked in the prompt only, not in the guard.
- Done later on 2 Nov: among Gemini's rewrites at 30% or below the one closest to the original's length is shown first (the lowest score breaks a tie). Not done: a third Gemini attempt.
- The diagnostic log stays out of the shared repo.

## 7. Scripts
`scripts/prompt_experiments_2026-11-02/` (see its `README.md`). They need the ReviewIt backend's Python and make no Gemini call.
