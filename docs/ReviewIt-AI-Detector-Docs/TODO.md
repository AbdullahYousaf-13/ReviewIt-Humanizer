# To-Do

Branch: `abdullah/humanizer-new-engine` (ReviewIt). Finished work is in `FIXED_ISSUES.md` and the test reports, not here.

## Before merging to main
- [ ] Supervisor approves the "Advanced" (Gemini) / "Standard" (Humarin, T5) tags (`rewrite-box.tsx`, `groupTag`; delete it if not approved)
- [ ] Ask Rana which login database the demo uses (repo again holds a DB password in `nodeBackend/.env.example`)

## Done today, to check by hand before the demo
- [ ] Humanize a flagged sentence that scores human alone (e.g. "Examples of Chatbots used in education…"): no "Recommended" copy of the original; rewrites shown when they exist
- [ ] Humanize an uncited sentence: Recommended + Options (Humarin / T5 / rule-based only at 30% or below)

## Prompt
- [ ] "need" became "must" (#21); "make vulnerable" became "weaken" (#73)
- [ ] Lowest score can pick the less faithful rewrite (#73)
- [ ] List and definition sentences still 100% (#25, #30, #31)
- [ ] Citation without a year ("Hao et al. examined…") not recognised as a citation
- [ ] Prompt + retry prompt checked on 10 sentences only (6 of 10 reached 30%)

## Ask the supervisor (after the demo)
- [ ] Gemini asked for 2 rewrites instead of 5: 6 vs 8 of 10 reached 30% on the same sentences
- [ ] Faster upload scoring: sort blocks by length + all CPU cores (about 38% faster, same scores)
