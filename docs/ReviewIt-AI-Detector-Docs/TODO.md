# To-Do

Branch: `abdullah/humanizer-new-engine` (ReviewIt). Finished work is in `FIXED_ISSUES.md` and the test reports, not here.

## Before merging to main
- [ ] Ask Rana which login database the demo uses (repo again holds a DB password in `nodeBackend/.env.example`)

## Prompt
- [ ] Prompt and citation fixes (28 Oct, `1974540`: need/should/may stay as strong, no one-word compression, uneven split for lists, "Name et al." is a citation) are tested offline only. Check them on the next Gemini run that happens anyway: #21 ("need" must not become "must"), #73 ("make more vulnerable" must not become "weaken"), the list sentences #25 / #31 / #35, "Hao et al. examined…"
- [ ] Some sentences never reach 30% with any prompt (#30, #32, #74, #136: 4 of 26 with 5 rewrites each). #30 already scores human alone, so keeping the original is right

## Ask the supervisor (after the demo)
- [ ] Faster upload scoring: sort blocks by length + all CPU cores (about 38% faster, same scores)
