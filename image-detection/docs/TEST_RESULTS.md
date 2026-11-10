# Test results

Date: 5 Nov 2026. Plan: [TEST_PLAN.md](TEST_PLAN.md). Cutoff 0.5 unless stated. Laptop CPU, 7.8 GB RAM.
Test set: **50 AI images** (ChatGPT, Gemini, Meta AI, Leonardo.ai, Recraft; 10 each) and **387 real photos** (Open Images, no people: 50 first set + 337 second set). Main version: **original files**, as downloaded.
Raw scores: `image-detection/results/*.csv`.

Column meaning: **Real flagged** = real photos wrongly called AI (lower is better). **AI caught** = of 50. **Correct** = of all images scored. **AUC** = ranking quality (1.0 perfect, 0.5 guessing).

## 1. Smaug (`abacusai/Smaug-AI-Image-Detector`)

| Test images | Real flagged | AI caught | Correct | AUC | Speed per image |
|---|---|---|---|---|---|
| OpenFake sample (50 + 50), smoke test | 1 of 50 | 47 of 50 | 96 of 100 | 0.989 | 14.3 s |
| Own set, JPEG re-save | 0 of 50 | 33 of 50 | 83 of 100 | 0.991 | 14.3 s |
| **Own set, original files** | **0 of 50** | **34 of 50** | **84 of 100** | **0.986** | 15.0 s |
| Own set, shrunk to 512 px | 2 of 50 | 38 of 50 | 86 of 100 | 0.978 | 12.8 s |
| Own set, screenshot-style 800 px PNG | 0 of 50 | 36 of 50 | 86 of 100 | 0.985 | not comparable* |
| **Second real set, original files (337 real)** | **2 of 337 (0.6%, range 0.2 to 2.1%)** | not applicable | 335 of 337 | not applicable | 13.9 s |

\* measured while other jobs were running.

AI images caught per tool (of 10 each):

| Own set version | ChatGPT | Gemini | Meta AI | Leonardo.ai | Recraft |
|---|---|---|---|---|---|
| JPEG re-save | 7 | 4 | 8 | 6 | 8 |
| Original files | 8 | 4 | 9 | 7 | 6 |
| Shrunk to 512 px | 8 | 5 | 7 | 8 | 10 |
| Screenshot-style | 8 | 6 | 9 | 7 | 6 |

## 2. Community Forensics (`OwensLab/commfor-model-384`)

Dropped from further tests after the first result. Loader check: the authors' 5 example images score 0.9988, 0.9878, 0.9569, 0.9516, 0.7860, identical to their notebook.

| Test images | Real flagged | AI caught | Correct | AUC | Speed per image |
|---|---|---|---|---|---|
| Own set, JPEG re-save | 0 of 50 | 5 of 50 | 55 of 100 | 0.869 | 0.4 s |

| Own set version | ChatGPT | Gemini | Meta AI | Leonardo.ai | Recraft |
|---|---|---|---|---|---|
| JPEG re-save | 0 | 0 | 2 | 2 | 1 |

## 3. Bombek1 (`Bombek1/ai-image-detector-siglip-dinov2`)

| Test images | Real flagged | AI caught | Correct | AUC | Speed per image |
|---|---|---|---|---|---|
| OpenFake sample, self-check (10 + 10) | 3 of 10 | 9 of 10 | 16 of 20 | 0.920 | 61 s |
| Own set, JPEG re-save | 6 of 50 | 50 of 50 | 94 of 100 | 0.986 | 47.7 s |
| **Own set, original files** | **7 of 50** | **50 of 50** | **93 of 100** | **0.990** | 43.6 s |
| **Second real set, original files (337 real)** | **49 of 337 (14.5%, range 11 to 19%)** | not applicable | 288 of 337 | not applicable | 43.6 s |

AI images caught per tool: 10 of 10 for all five tools, in both versions.

Loader check: the app's `bombek1.py` reproduces the research script on the 20 self-check images (16 of 20, 9 of 10, 3 of 10, AUC 0.920).

## 4. Combined (Smaug + Bombek1), original files

Combined score = average of the two models' log-odds, equal weights. 50 AI images, 387 real photos. The cutoff is set from real photos only; the AI images only measure the catch rate.

**4a. Methods compared on all 387 real photos** (AI caught when the cutoff lets through the stated number of real photos)

| Method | AUC | 1% (3 real) | 2% (7 real) | 5% (19 real) | 10% (38 real) |
|---|---|---|---|---|---|
| Smaug alone | 0.987 | 40 of 50 | 42 of 50 | 49 of 50 | 49 of 50 |
| Bombek1 alone | 0.988 | 37 of 50 | 42 of 50 | 47 of 50 | 49 of 50 |
| **Combined** | **0.996** | **41 of 50** | **46 of 50** | **50 of 50** | **50 of 50** |

**4b. Cutoff set on the cutoff part (97 real photos), tested on the final part (290 real photos)**

| Method | False-alarm limit | Real flagged (final) | AI caught |
|---|---|---|---|
| Smaug alone | 1% | 0 of 290 (range 0 to 1.3%) | 22 of 50 (44%, range 31 to 58%) |
| Bombek1 alone | 1% | 3 of 290 (1.0%, range 0.4 to 3.0%) | 37 of 50 (74%, range 60 to 84%) |
| **Combined** | **1%** | **0 of 290 (range 0 to 1.3%)** | **31 of 50 (62%, range 48 to 74%)** |
| Smaug alone | 2% | 4 of 290 (1.4%) | 42 of 50 (84%) |
| Bombek1 alone | 2% | 7 of 290 (2.4%) | 43 of 50 (86%) |
| **Combined** | **2%** | **4 of 290 (1.4%, range 0.5 to 3.5%)** | **46 of 50 (92%, range 81 to 97%)** |
| Smaug alone | 5% | 7 of 290 (2.4%) | 45 of 50 (90%) |
| Bombek1 alone | 5% | 7 of 290 (2.4%) | 44 of 50 (88%) |
| **Combined** | **5%** | **8 of 290 (2.8%, range 1.4 to 5.3%)** | **50 of 50 (100%, range 93 to 100%)** |

The 0.5% and 1% limits give the same cutoff because the cutoff part has only 97 real photos.

**4c. Three bands** (combined score; likely AI above 2.27, likely real below -3.42; cutoffs from the cutoff part)

| | Likely AI | Unclear | Likely real |
|---|---|---|---|
| Real photos, final part (290) | 0 | 13 | 277 |
| AI images (50) | 31 | 19 | 0 |

**4d. AI images caught per tool** at the 1% cutoff (of 10 each)

| ChatGPT | Gemini | Meta AI | Leonardo.ai | Recraft |
|---|---|---|---|---|
| 8 | 4 | 9 | 6 | 4 |

## 5. Format check: real photos saved as PNG and WEBP

50 real photos, original JPEG against the same photo re-saved as PNG (lossless) and WEBP (quality 90). These are converted copies, not originals. Cutoffs from 4c.

| Format | Smaug above 0.5 | Bombek1 above 0.5 | Combined above the 1% cutoff | Combined above the 10% cutoff | Mean change of combined score | Largest increase |
|---|---|---|---|---|---|---|
| JPEG (original) | 0 of 50 | 7 of 50 | 0 of 50 | 3 of 50 | 0 | 0 |
| PNG | 0 of 50 | 7 of 50 | 0 of 50 | 3 of 50 | -0.04 | +0.17 |
| WEBP | 0 of 50 | 8 of 50 | 0 of 50 | 9 of 50 | +0.27 | +1.57 |

## 6. Comparison (original files)

| | Smaug | Bombek1 | Combined |
|---|---|---|---|
| Real flagged at 0.5 (of 387) | 2 | 56 (14.5%) | not applicable |
| AI caught at 0.5 (of 50) | 34 | 50 | not applicable |
| AUC (387 real, 50 AI) | 0.987 | 0.988 | 0.996 |
| AI caught at 1% / 2% / 5% real flagged | 40 / 42 / 49 | 37 / 42 / 47 | 41 / 46 / 50 |
| Speed per image | 14 s | 44 s | 58 s |

## 7. Band limits and decision

500 random splits of the 387 real photos (25% cutoff part, 75% final part); the 50 AI images are resampled each time. Combined score, original files. Mean (5th to 95th percentile). Script: `analyze_layouts.py`.

| Accuse / clear limit | Real photos accused | Real photos cleared | AI accused | AI left unclear | AI wrongly cleared |
|---|---|---|---|---|---|
| 1% / 5% | 1.1% (0 to 3.8) | 94.9% (90.3 to 98.6) | 75.7% (54 to 100) | 23.8% | 0.5% (0 to 4.0) |
| 1% / 10% | 1.1% (0 to 3.8) | 89.8% (83.8 to 94.8) | 75.7% (54 to 100) | 24.3% | 0% |
| **2% / 5% (chosen)** | **2.1% (0 to 5.5)** | **94.9% (90.3 to 98.6)** | **89.4% (66 to 100)** | **10.1%** | **0.5% (0 to 4.0)** |
| 2% / 10% | 2.1% (0 to 5.5) | 89.8% (83.8 to 94.8) | 89.4% (66 to 100) | 10.6% | 0% |
| 5% / 10% | 5.1% (1.4 to 9.7) | 89.8% (83.8 to 94.8) | 99.5% (96 to 100) | 0.5% | 0% |
| 5% / 20% | 5.1% (1.4 to 9.7) | 79.5% (72.1 to 86.2) | 99.5% (96 to 100) | 0.5% | 0% |

The single-split numbers in 4b are lower than these averages (for example 1.4% at the 2% limit) because that split gave a cautious cutoff; use this table.

**Decision (5 Nov 2026)**

| Setting | Value | Reason |
|---|---|---|
| Combined score | Average of Smaug and Bombek1 log-odds, equal weights | AUC 0.996 against 0.987 and 0.988; 46 of 50 AI caught at 2% against 42 for each model alone |
| Accuse limit | **2%** | Accusing a paying customer is the worst failure. 1% to 2% adds 13.7 points of AI accused for 1.0 point of real photos accused; 2% to 5% adds 10.1 points for 3.0 points |
| Clear limit | **5%, for now** | Chosen by the user. Clears 94.9% of real photos; risk: 0.5% of AI images wrongly cleared on average, up to 4% in the worst 5% of splits. 10% gave 0% wrongly cleared but cleared 89.8% |
| Default cutoffs | Accuse -1.74, clear -3.16 | Computed from all 387 real photos; both limits are settings |

Share of "likely AI" verdicts that are really AI, from the means above:

| Accuse limit | If 5% of uploads are AI | If 20% of uploads are AI |
|---|---|---|
| 1% | 78% | 95% |
| 2% | 69% | 91% |
| 5% | 51% | 83% |

Bands with the default cutoffs, on all 387 real photos and 50 AI images (in-sample, optimistic):

| | Likely AI | Unclear | Likely real |
|---|---|---|---|
| Real photos (387) | 7 | 12 | 368 |
| AI images (50) | 46 | 4 | 0 |

## 8. Speed: Bombek1 SigLIP half in bf16 vs float32 (CPU)

The laptop CPU (i5-8250U, AVX2, no bf16 hardware) is slow in bf16.

| | bf16 | float32 |
|---|---|---|
| Bombek1 seconds per photo | 49.6 | 12.2 (4.08 times faster) |
| Score difference | | within 0.04 log-odds |
| Bands on 3 photos | | unchanged |
| Photos within 0.02 of a cutoff (of 437) | | 2 |

Float32 is now the default on CPU (`bombek1.py`).

## 9. End to end through the app (`POST /api/imagedetector/detect`)

| Image | Label | Score (research score) | Seconds |
|---|---|---|---|
| real/flower_04.jpg | Unclear | -3.07 (-3.08) | 32.7 |
| fake/gemini__flower-2.jpg | Unclear | -1.86 (-1.87) | 29.5 |
| real/mountain_01.jpg | Original | -6.29 (-6.08) | 26.6 |
| fake/chatgpt__mountain-1.png | AI | +6.55 (+6.56) | 25.0 |

Models ready 80 s after start. A second request sent during a check got 429. No file gave 400; txt and HEIC gave 415.

## Limits

- 50 AI images: the catch rate has a range of about 10 points. 387 real photos: a false-alarm rate of 0 of 290 allows a true rate up to about 1.3%.
- Earlier combined results on 50 real photos (AUC 0.999, no overlap) were optimistic; with 387 real photos the combined AUC is 0.996.
- Open Images may be in the models' training data, so false alarms may be understated. The AI images contain no people, so catch rates for AI images with people are unmeasured.
- Format check copies are JPEGs re-saved as PNG or WEBP, not native PNG or WEBP photos.
- Scores of the first 100 images are rounded to 4 decimals; later scores have 6.
- Community Forensics and Bombek1 were first run on the JPEG re-save version only; Bombek1 was later also run on original files.
