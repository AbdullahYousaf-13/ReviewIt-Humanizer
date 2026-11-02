# To-Do

Last updated 2026-11-02. Branch: `abdullah/humanizer-new-engine` (ReviewIt). Finished work is in `FIXED_ISSUES.md` and the test reports, not here.

## Main goal: 90% or more of the flagged sentences at 30% or below
- [ ] Fix the prompts for the sentences that stay above 30% (Kumasi, succession planning, data collection, reflexive analysis). The next run logs the full text of every candidate; compare what the failing sentences' rewrites have in common with the passing ones

## Measure the 2 Nov changes on a live Gemini run (a paid run, started by you)
- [ ] The same 16 sentences (listed in `RETRY_AND_FIRST_CALL_EXPERIMENTS_2026-11-02.md`), at least twice, with the diagnostic log on: the new first call (2 ordinary + 3 spelled out) and the retry (5 spelled out). Compare with the earlier runs; runs differ a lot (`OPEN_ISSUES.md` B5), so judge a change on two runs, not one.
- [ ] If the retry rescues fewer sentences than the earlier 5 of 6 in two more runs, take the faithfulness rule out of the retry prompt first (the likeliest cause, not proven), then the word range
- [ ] Check the winners of the spelled-out first-call rewrites for drift, as was done for 5 retry rewrites (3 faithful, 1 drift, 1 borderline)

## Decisions for you
- [ ] Among rewrites at 30% or below, show the one closest to the original's length instead of the lowest score (`OPEN_ISSUES.md` B6). It changes which rewrite the page recommends, so it was left out on 2 Nov
- [ ] A third Gemini attempt for sentences that still fail: about $0.002 each, and no gain is expected for the sentences that fail every rewrite (B4); not built

## Before anything goes to main
- [ ] Ask first. The two local `log:` commits (run-time `par=` line and the `[humanizer-diag]` log) are not approved for the shared repo: push only the `prompt:` commits, and drop them before a merge
- [ ] Docs stay in `ReviewIt-Humanizer/docs` only

## Prompt (tested offline only, check on the next Gemini run that happens anyway)
- [ ] Cause words, duty-becomes-action, negation, direction, bracketed phrase and acronym rules added to the hard rules (29 Oct, `f543cfe`): #118 must not become "made students more likely", #24 must not become "warn users"
- [ ] A sentence with a citation stays one sentence (29 Oct, `a603eef`), and no new person or group is added (#25, #26, #30 in the 28 Oct run)
- [ ] Still high when scored alone after humanizing: #136, #27, #117 (abstract-noun sentences, not lists). Hidden inside low-scoring blocks, no reliable prompt fix known

## Ask the supervisor (after the demo)
- [ ] Faster upload scoring: sort blocks by length + all CPU cores (about 38% faster, same scores)
