# To-Do

Branch: `abdullah/humanizer-new-engine` (ReviewIt). Finished work is in `FIXED_ISSUES.md` and the test reports, not here.

## Prompt (tested offline only, check on the next Gemini run that happens anyway)
- [ ] Cause words, duty-becomes-action, negation, direction, bracketed phrase and acronym rules added to the hard rules (29 Oct, `f543cfe`): #118 must not become "made students more likely", #24 must not become "warn users"
- [ ] A sentence with a citation stays one sentence (29 Oct, `a603eef`), and no new person or group is added (#25, #26, #30 in the 28 Oct run)
- [ ] Still high when scored alone after humanizing: #136, #27, #117 (abstract-noun sentences, not lists). Hidden inside low-scoring blocks, no reliable prompt fix known (see B8)

## Ask the supervisor (after the demo)
- [ ] Faster upload scoring: sort blocks by length + all CPU cores (about 38% faster, same scores)
