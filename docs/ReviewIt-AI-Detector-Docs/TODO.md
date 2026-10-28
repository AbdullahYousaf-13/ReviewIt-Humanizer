# To-Do

Branch: `abdullah/humanizer-new-engine` (ReviewIt). Finished work is in `FIXED_ISSUES.md` and the test reports, not here.

## Before merging to main
- [ ] Supervisor approves the "Advanced" (Gemini) / "Standard" (Humarin, T5) tags (`rewrite-box.tsx`, `groupTag`; delete it if not approved)
- [ ] Ask Rana which login database the demo uses (repo again holds a DB password in `nodeBackend/.env.example`)

## Prompt
- [ ] Prompt and citation fixes (28 Oct, `1974540`: need/should/may stay as strong, no one-word compression, uneven split for lists, "Name et al." is a citation) are tested offline only. Check them on the next Gemini run that happens anyway: #21 ("need" must not become "must"), #73 ("make more vulnerable" must not become "weaken"), the list sentences #25 / #31 / #35, "Hao et al. examined…"
- [ ] Lowest score can pick the less faithful rewrite (#73): left for now (your decision)
- [ ] Some sentences never reach 30% with any prompt (#30, #32, #74, #136: 4 of 26 with 5 rewrites each). #30 already scores human alone, so keeping the original is right

## Ask the supervisor (after the demo)
- [ ] First-call success depends on the number of rewrites. Latest prompt, 26 sentences, 130 rewrites: 1 rewrite 43%, **2 rewrites 62%**, 3 rewrites 73%, **5 rewrites 85%** (90% needs about 7). On the 10-sentence test, 2 rewrites gave 6 of 10 after the retry, against 8 of 10 with 5. Five rewrites cost about the same per sentence ($0.0015 vs $0.0016 with retries) and are faster (3.8 s vs 5.2 s)
- [ ] Faster upload scoring: sort blocks by length + all CPU cores (about 38% faster, same scores)
