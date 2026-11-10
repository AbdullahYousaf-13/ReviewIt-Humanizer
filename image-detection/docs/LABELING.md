# How an image gets its label

Code: `backend/imagedetector/service.py` (checks, label names), `combined.py` (score, bands), `detector.py` (Smaug), `bombek1.py` (Bombek1).

## Steps

| Step | What happens | Result if it fails |
|---|---|---|
| 1. Upload | `POST /api/imagedetector/detect`, form field `file`. No file | 400 |
| 2. File type | Extension must be `.jpg .jpeg .png .webp .bmp .tif .tiff`. `.heic` and `.heif` are named in the message | 415 |
| 3. Not empty | The file must have bytes | 400 |
| 4. Readable | Pillow opens and verifies it | 415 |
| 5. One at a time | If another image is being checked | 429 `BUSY` |
| 6. Read once | The image is read into memory (nothing is saved to disk) and shared by both models | |
| 7. Smaug | Returns `p_smaug`, the probability the image is AI (0 to 1). Runs with 3 crops | |
| 8. Bombek1 | Converts the image to RGB, runs SigLIP2 and DINOv2 (LoRA), returns `p_bombek1` (0 to 1, sigmoid of its output). SigLIP half runs in float32 on CPU | |
| 9. Log-odds | For each model: `logit(p) = ln(p / (1 - p))`, with p kept inside 0.000001 to 0.999999 | |
| 10. Combined score | `score = (logit(p_smaug) + logit(p_bombek1)) / 2` (equal weights) | |
| 11. Band | See the table below | |
| 12. Answer | `label`, `score` (2 decimals), cutoffs, each model's probability and verdict, seconds | |

## Bands (step 11)

| Combined score | Label |
|---|---|
| above -1.74 | **AI** |
| above -3.16, up to -1.74 | **Unclear** |
| -3.16 or below | **Original** |

Each model's own verdict in the answer is separate from the label: `AI` at probability 0.5 or more, otherwise `Original`. The label uses only the combined score.

## Where the cutoffs come from

| Cutoff | Rule | Value |
|---|---|---|
| Accuse (-1.74) | At most 2% of the 387 real photos score above it | -1.74 |
| Clear (-3.16) | At most 5% of the 387 real photos score above it | -3.16 |

- Real photos only (Open Images, original files, scored with both models); the AI images were not used to set them.
- Both are settings: `IMAGE_ACCUSE_CUTOFF`, `IMAGE_CLEAR_CUTOFF`.
- Why 2%: wrongly accusing a customer is the worst failure.

## Expected results (500 random splits of our test set)

| | Share |
|---|---|
| Real photos labelled AI | 2.1% (5th to 95th percentile 0 to 5.5%) |
| Real photos labelled Original | 94.9% |
| AI images labelled AI | 89.4% |
| AI images labelled Original | 0.5% (0 to 4.0%) |

## Worked example

Smaug 0.206 gives logit -1.35. Bombek1 0.335 gives logit -0.69. Score = (-1.35 + -0.69) / 2 = -1.02. That is above -1.74, so the label is **AI**, although each model alone says `Original`.

## Limits

- The label is a hint, not proof; never accuse a customer on it alone.
- Tested on photos without people, and on five generators; screenshots and graphics were not tested (a receipt screenshot was labelled AI, score -1.02).
- Real photos saved as WEBP score higher than JPEG or PNG.
