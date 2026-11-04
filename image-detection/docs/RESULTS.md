# AI image detector: results of all tests

Cutoff 0.5, laptop CPU. Own set = 50 real photos (Open Images) + 50 AI images (ChatGPT, Gemini, Meta AI, Leonardo, Recraft). Plan: [TEST_PLAN.md](TEST_PLAN.md).

## All tests

| # | Model | Test images | Real wrongly called AI | AI caught | Correct | AUC | Speed / image |
|---|---|---|---|---|---|---|---|
| 1 | Smaug | OpenFake sample (50 + 50), smoke test | 1/50 | 47/50 | 96/100 | 0.989 | 14.3 s |
| 2 | **Smaug** | **Own set, JPEG re-save (main)** | **0/50** | **33/50** | **83/100** | **0.991** | 14.3 s |
| 3 | Smaug | Own set, original files | 0/50 | 34/50 | 84/100 | 0.986 | 15.0 s |
| 4 | Smaug | Own set, shrunk to 512 px | 2/50 | 38/50 | 86/100 | 0.978 | 12.8 s |
| 5 | Smaug | Own set, screenshot-style | 0/50 | 36/50 | 86/100 | 0.985 | 14 s* |
| 6 | Community Forensics | Own set, JPEG re-save | 0/50 | 5/50 | 55/100 | 0.869 | 0.4 s |
| 7 | Bombek1 | OpenFake sample, self-check (10 + 10) | 3/10 | 9/10 | 16/20 | 0.920 | 61 s |
| 8 | **Bombek1** | **Own set, JPEG re-save** | **6/50** | **50/50** | **94/100** | **0.986** | 47.7 s |

\* measured while other jobs were running.

## AI images caught per tool (own set, JPEG re-save, of 10 each)

| Tool | Smaug | Community Forensics | Bombek1 |
|---|---|---|---|
| Meta AI | 8 | 2 | 10 |
| Recraft | 8 | 1 | 10 |
| ChatGPT | 7 | 0 | 10 |
| Leonardo.ai | 6 | 2 | 10 |
| Gemini | 4 | 0 | 10 |

Real photos wrongly called AI by Bombek1 (6): flower_04, animal_03, flower_02, forest_04, mountain_03, coast_05 (scores 0.58 to 0.93).

## Models

| Model | Size | Licence | In ReviewIt |
|---|---|---|---|
| Smaug | 439M parameters | Apache 2.0 | `detector.py` (merged) |
| Community Forensics | 22M parameters | MIT | `commfor.py` (branch) |
| Bombek1 | 740M parameters | MIT | `bombek1.py` (branch) |

## Notes

- Smaug: no real photo flagged, about two thirds of AI images caught (cautious).
- Bombek1: every AI image caught (50/50), but 6 of 50 real photos (12%, 95% range 6 to 24%) wrongly called AI (aggressive). Best overall score, slowest (about 48 s per image).
- Community Forensics: fast but catches only 10% at 0.5.
- Not yet tested: combining models.
- Small sample (50 + 50). Open Images may be in the models' training data.
