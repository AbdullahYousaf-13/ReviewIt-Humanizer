# 04 Test results

Date: 4 Nov 2026. Plan: [02_TEST_PLAN.md](02_TEST_PLAN.md). Cutoff 0.5 unless stated. Laptop CPU, 7.8 GB RAM.
Test set: 50 real photos + 50 AI images (ChatGPT, Gemini, Meta AI, Leonardo.ai, Recraft; 10 each). Main version: JPEG re-save.
Raw scores: `image-detection/results/*.csv`.

Column meaning: **Real flagged** = real photos wrongly called AI (of 50, lower is better). **AI caught** = of 50. **Correct** = of 100. **AUC** = ranking quality (1.0 perfect, 0.5 guessing).

## 1. Smaug (`abacusai/Smaug-AI-Image-Detector`)

| Test images | Real flagged | AI caught | Correct | AUC | Speed per image |
|---|---|---|---|---|---|
| OpenFake sample (50 + 50), smoke test | 1 | 47 | 96 | 0.989 | 14.3 s |
| **Own set, JPEG re-save (main)** | **0** | **33** | **83** | **0.991** | 14.3 s |
| Own set, original files | 0 | 34 | 84 | 0.986 | 15.0 s |
| Own set, shrunk to 512 px | 2 | 38 | 86 | 0.978 | 12.8 s |
| Own set, screenshot-style 800 px | 0 | 36 | 86 | 0.985 | not comparable* |

\* measured while other jobs were running.

AI images caught per tool (of 10 each):

| Own set version | ChatGPT | Gemini | Meta AI | Leonardo.ai | Recraft |
|---|---|---|---|---|---|
| JPEG re-save | 7 | 4 | 8 | 6 | 8 |
| Original files | 8 | 4 | 9 | 7 | 6 |
| Shrunk to 512 px | 8 | 5 | 7 | 8 | 10 |
| Screenshot-style | 8 | 6 | 9 | 7 | 6 |

Final part only (30 + 30), JPEG re-save, cutoff tuned on the tuning part (0.029): AI caught 21/30 (70%, range 52 to 83%), real flagged 0/30 (range 0 to 11%). At cutoff 0.5: AI caught 16/30 (53%).

## 2. Community Forensics (`OwensLab/commfor-model-384`)

Loader check: the authors' 5 example images score 0.9988, 0.9878, 0.9569, 0.9516, 0.7860, identical to their notebook.

| Test images | Real flagged | AI caught | Correct | AUC | Speed per image |
|---|---|---|---|---|---|
| Own set, JPEG re-save | 0 | 5 | 55 | 0.869 | 0.4 s |

| Own set version | ChatGPT | Gemini | Meta AI | Leonardo.ai | Recraft |
|---|---|---|---|---|---|
| JPEG re-save | 0 | 0 | 2 | 2 | 1 |

## 3. Bombek1 (`Bombek1/ai-image-detector-siglip-dinov2`)

| Test images | Real flagged | AI caught | Correct | AUC | Speed per image |
|---|---|---|---|---|---|
| OpenFake sample, self-check (10 + 10) | 3 of 10 | 9 of 10 | 16 of 20 | 0.920 | 61 s |
| **Own set, JPEG re-save** | **6** | **50** | **94** | **0.986** | 47.7 s |

| Own set version | ChatGPT | Gemini | Meta AI | Leonardo.ai | Recraft |
|---|---|---|---|---|---|
| JPEG re-save | 10 | 10 | 10 | 10 | 10 |

Real photos wrongly called AI (6 of 50, 12%, 95% range 6 to 24%):

| Photo | Score |
|---|---|
| flower_04 | 0.926 |
| animal_03 | 0.883 |
| flower_02 | 0.835 |
| forest_04 | 0.806 |
| mountain_03 | 0.749 |
| coast_05 | 0.575 |

Loader check: the app's `bombek1.py` reproduces the research script on the 20 self-check images (16/20, 9/10, 3/10, AUC 0.920).

## 4. Combined (Smaug + Bombek1; Community Forensics where stated)

Combined score = square root of (Smaug score x Bombek1 score). Own set, JPEG re-save. Exploratory: uses the saved scores above, no new runs.

**4a. Fixed rules at cutoff 0.5, all 100 images (nothing tuned)**

| Rule | Real flagged | AI caught | Correct | AUC |
|---|---|---|---|---|
| Smaug alone | 0 | 33 | 83 | 0.991 |
| Bombek1 alone | 6 | 50 | 94 | 0.986 |
| Both agree (Smaug and Bombek1 at least 0.5) | 0 | 33 | 83 | not applicable |
| Either (Smaug or Bombek1 at least 0.5) | 6 | 50 | 94 | not applicable |
| Average of Smaug and Bombek1 | 0 | 40 | 90 | 0.992 |
| Average of all three models | 0 | 33 | 83 | 0.992 |
| **Combined score** | **0** | **37** | **87** | **0.999** |

AUC for the two single models is from the scoring runs; for the combinations it is computed from the saved scores (rounded to 4 decimals), so the last digit may differ by 0.001.

**4b. Cutoff chosen on the 20 + 20 tuning images, reported on the 30 + 30 final images**

Choice rule: at most 1 of 20 real photos flagged in tuning, then the most AI caught.

| Rule | Cutoff | Real flagged (final) | AI caught (final) |
|---|---|---|---|
| Smaug alone | 0.017 | 0/30 (range 0 to 11%) | 22/30, 73% (range 56 to 86%) |
| Bombek1 alone | 0.671 | 4/30, 13% (range 5 to 30%) | 28/30, 93% (range 79 to 98%) |
| Average of Smaug and Bombek1 | 0.500 | 0/30 (range 0 to 11%) | 20/30, 67% (range 49 to 81%) |
| Average of all three models | 0.323 | 0/30 (range 0 to 11%) | 23/30, 77% (range 59 to 88%) |
| **Combined score** | **0.096** | **0/30 (range 0 to 11%)** | **24/30, 80% (range 63 to 90%)** |

**4c. Cutoff sweep for the combined score, all 100 images (cutoff picked after seeing the data: optimistic, not a result)**

| Cutoff | Real flagged | AI caught |
|---|---|---|
| 0.02 | 2 | 49 |
| 0.05 | 0 | 46 |
| 0.10 | 0 | 44 |
| 0.20 | 0 | 39 |
| 0.30 | 0 | 39 |
| 0.50 | 0 | 37 |

Speed of the combination: about 62 s per image (Smaug 14 s + Bombek1 48 s).

## 5. Comparison (own set, JPEG re-save, cutoff 0.5, all 100 images)

| | Smaug | Community Forensics | Bombek1 | Combined score |
|---|---|---|---|---|
| Real flagged (of 50) | 0 | 0 | 6 | 0 |
| AI caught (of 50) | 33 | 5 | 50 | 37 |
| Correct (of 100) | 83 | 55 | 94 | 87 |
| AUC | 0.991 | 0.869 | 0.986 | 0.999 |
| Speed per image | 14 s | 0.4 s | 48 s | 62 s |

## Limits

- 50 + 50 images; final part 30 + 30. Ranges are 95% Wilson intervals.
- Open Images may be in the models' training data, so false alarms may be understated.
- Combination rules and cutoffs in 4a and 4c use all 100 images and are optimistic; 4b is the fair test.
- Community Forensics and Bombek1 were run on the JPEG re-save version only.
