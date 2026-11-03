# Smaug-AI-Image-Detector: validation results

Date: 3 Nov 2026. Test: [TEST_PLAN.md](TEST_PLAN.md). Model: `abacusai/Smaug-AI-Image-Detector`, CPU, 3 crops per image (about 14 s per image).
Scripts: `scripts/build_testset.py` (split and the four versions), `scripts/score_smaug.py` (scoring), `scripts/analyze_results.py` (this report).
Raw scores: `results/smaug_own_<version>_crops3.csv`. Full printout: `results/smaug_own_report.txt`.

## Test set

50 real photos (Open Images, 2018 Flickr, no people) + 50 AI images (ChatGPT, Gemini, Meta AI, Leonardo.ai, Recraft; 10 each), same 10 subjects.
Copilot and Ideogram were dropped because their free tiers do not allow 10 images.
Split: tuning 20 real + 20 AI (used only to choose the cutoff), final 30 real + 30 AI (used to report).
Every version below applies the same processing to real and AI images.

## Result on the 30 real + 30 AI final images

| Version | AUC | AI caught at 0.5 | AI caught at tuned cutoff | Real photos flagged (0.5 / tuned) |
|---|---|---|---|---|
| **JPEG re-save q85 (main)** | 0.992 | 53% (16/30, 95% range 36-70%) | 70% (21/30, 52-83%), cutoff 0.029 | 0/30 / 0/30 |
| Original files | 0.985 | 57% (17/30, 39-73%) | 70% (21/30, 52-83%), cutoff 0.037 | 0/30 / 0/30 |
| Shrunk to 512 px | 0.975 | 67% (20/30, 49-81%) | 77% (23/30, 59-88%), cutoff 0.040 | 0/30 / 0/30 |
| Screenshot-style 800 px PNG | 0.981 | 60% (18/30, 42-75%) | 73% (22/30, 56-86%), cutoff 0.044 | 0/30 / 1/30 (3.3%, 1-17%) |

All 50 real photos, JPEG re-save, cutoff 0.5: 0 flagged (0/50). All 50 AI images: 33 caught (66%).
Caught per tool (all 10 each, cutoff 0.5, JPEG re-save): Meta AI 8, Recraft 8, ChatGPT 7, Leonardo 6, Gemini 4.

## What it means

- **No false alarms at the default cutoff.** Real photos all score below about 0.005. At 30 real photos the true false-alarm rate could still be up to about 11%.
- **It misses a lot of AI images.** About half to two thirds are caught at 0.5, depending on the version. The ranking is very good (AUC 0.975 to 0.992): the AI images it misses score close to the real photos, not in between.
- **File format is not the clue.** Original files and JPEG re-save give nearly the same result.
- **Shrinking or screenshots do not break it.** Differences are within the 95% ranges.
- **A cutoff chosen from 20 AI images is unreliable.** The tuning set picked 0.03 to 0.04 each time (the score of its weakest AI image). That sits right on top of where real photos score, and it flagged 2 of 20 real tuning photos at 512 px and 1 of 30 final real photos in the screenshot version. Do not promise a number from this cutoff.
- **Misses are mostly landscapes and animals** (forest, mountain, animal, flower) and Gemini images are the hardest. The cause (subject, generator or both) is not known.

## Caveats

- 30 + 30 final images is a small sample; every rate has a wide range.
- Open Images may be in Smaug's training data, so the false-alarm rate could look better than it really is.
- Single run, one prompt variant per tool; the AI images come from five free tiers and are not a full picture of what customers upload.
- The speed (14 s per image on a laptop CPU) is too slow for a live service without a GPU or one crop per image.

## Next steps

Compare Community Forensics (`OwensLab/commfor-model-384`, MIT) and Bombek1 (`Bombek1/ai-image-detector-siglip-dinov2`, MIT) on the same split, and test whether combining models catches more AI images without false alarms.
