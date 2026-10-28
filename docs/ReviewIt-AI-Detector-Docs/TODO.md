# To-Do

Branch: `abdullah/humanizer-new-engine` (ReviewIt). Finished work is in `FIXED_ISSUES.md` and the test reports, not here.

## Before merging to main
- [ ] Supervisor approves the "Advanced" (Gemini) / "Standard" (Humarin, T5) tags (`rewrite-box.tsx`, `groupTag`; delete it if not approved)
- [ ] Ask Rana which login database the demo uses (repo again holds a DB password in `nodeBackend/.env.example`)

## Waiting for your decision
- [ ] Original score: don't re-score the original sentence alone, use the document's score. Needs one new optional **request** field `original_score` + the page sends it (3 calls). API is locked: your OK first
- [ ] Page: when the backend returns the original unchanged (`engine: "original"`), show no "Recommended" copy
- [ ] Rule-based = a local engine like Humarin / T5: shown only at 30% or below, ordered with them, never "Recommended" by default

## Prompt
- [ ] "need" became "must" (#21); "make vulnerable" became "weaken" (#73)
- [ ] Lowest score can pick the less faithful rewrite (#73)
- [ ] List and definition sentences still 100% (#25, #30, #31)
- [ ] Citation without a year ("Hao et al. examined…") not recognised as a citation
- [ ] Prompt + retry prompt checked on 10 sentences only (6 of 10 reached 30%)

## Ask the supervisor (after the demo)
- [ ] Gemini asked for 2 rewrites instead of 5: 6 vs 8 of 10 reached 30% on the same sentences
- [ ] Faster upload scoring: sort blocks by length + all CPU cores (about 38% faster, same scores)
