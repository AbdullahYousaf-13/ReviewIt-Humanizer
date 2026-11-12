# Model research: AI-generated image detectors

Date: 3 Nov 2026, updated 5 Nov 2026. Results of testing: [TEST_RESULTS.md](TEST_RESULTS.md). Plan: [TEST_PLAN.md](TEST_PLAN.md). All models on one page: [MODELS.md](../../MODELS.md).

## Constraints

| Item | Decision |
|---|---|
| Models | Open-source, run locally. No paid detection APIs |
| Licence | Apache 2.0 or MIT only (ReviewIt is a paid product: $6.99 per document, $59 per month) |
| Hardware | Laptop CPU now (7.8 GB RAM), GPU possible later |
| Focus | AI-generated images. AI-edited photos, screenshots and artwork are secondary |
| Choice | Single model or combination, whichever scores best on our own test set. **Result: a combination of Smaug and Bombek1** |

## Shortlist (tested)

| Model | Hugging Face id | Parameters | Weights | Licence | Architecture |
|---|---|---|---|---|---|
| Smaug | `abacusai/Smaug-AI-Image-Detector` | 439M | 0.88 GB | Apache 2.0 | EmbeddingGemma-2 image encoder + linear classifier |
| Community Forensics | `OwensLab/commfor-model-384` | 21.8M | 0.09 GB | MIT (code and weights) | ViT small, 384 px input |
| Bombek1 | `Bombek1/ai-image-detector-siglip-dinov2` | 740M | 2.1 GB | MIT | SigLIP2-SO400M + DINOv2-Large, LoRA adapters, MLP head |

| Model | Custom code needed | Extra packages | Base models (licence) |
|---|---|---|---|
| Smaug | `smaug_image_detect.py` (in model repo) | `sentence-transformers[image]`, transformers 5.20.0 | none |
| Community Forensics | none (own loader, timm architecture) | `timm` | `vit_small_patch16_384` (Apache 2.0, architecture only) |
| Bombek1 | `model.py` (in model repo) | `timm`, `peft` | `google/siglip2-so400m-patch14-384` (Apache 2.0), `vit_large_patch14_dinov2.lvd142m` (Apache 2.0) |

## Outcome after testing (own test set, original files; details in TEST_RESULTS.md)

| Model | Result at cutoff 0.5 | Decision | Code in ReviewIt (`backend/imagedetector/`) |
|---|---|---|---|
| Smaug | 2 of 387 real photos flagged; 34 of 50 AI caught; AUC 0.987 | Keep | `detector.py`, merged to main |
| Community Forensics | 5 of 50 AI caught (JPEG copy); AUC 0.869 | Dropped | `commfor.py`, on branch `abdullah/image-detector`, not merged |
| Bombek1 | 56 of 387 real photos flagged (14.5%); 50 of 50 AI caught; AUC 0.988 | Keep, for the combination | `bombek1.py`, on branch `abdullah/image-detector`, not merged |
| **Combined (average of Smaug and Bombek1 log-odds)** | AUC 0.996; 41, 46 and 50 of 50 AI caught when 1%, 2% and 5% of real photos are let through | **Best method** (accuse limit 2%, clear limit 5%, three bands) | `combined.py`, on branch `abdullah/image-detector`, not merged |

- Confirmed: Bombek1 flags many real photos (card and Smaug's table said so).
- Confirmed: Community Forensics runs on CPU (0.4 s per image) but is too weak at 0.5.
- Smaug is the most cautious (few false alarms, misses about a third of AI images at 0.5); Bombek1 the most aggressive.

## Model details

| Item | Smaug | Community Forensics | Bombek1 |
|---|---|---|---|
| Trained on | Mixed generators incl. GPT-Image 2, Nano Banana Pro, Midjourney 7, FLUX.2, Recraft, Ideogram, DALL·E 3, Firefly 3; resized, recompressed and blurred images; professional photos as hard negatives | 2.7M images from 4,803 generators (CVPR 2025) | OpenFake, about 95K images, with JPEG, blur, noise and resize augmentation |
| Output | Probability 0 to 1, default cutoff 0.5; `crops=1` is 3x faster | Sigmoid probability | Sigmoid probability |
| Stated limits | New or evasion-tuned generators may pass; small AI-edited regions may score as real | Weaker on Reddit-style real-world images (AUC 0.744 in Smaug's table) | Many false alarms on real photos (card: about 9% on COCO-style; Smaug's table: 34.7% on Reddit); poor below 128x128 px and on screenshots |

## Independent benchmark

Ren et al., arXiv 2602.07814 (Feb 2026): 16 detectors, 12 datasets, about 2.6M images, 291 generators. Smaug was not included.

| Detector | Mean accuracy | Median |
|---|---|---|
| Community-Forensics | 0.780 | 0.821 |
| DRCT CLIP-ViT (SD v2.0) | 0.718 | 0.696 |
| SAFE | 0.688 | 0.812 |
| PatchCraft | 0.675 | 0.742 |
| UnivFD | 0.407 | 0.497 |
| CNNSpot | 0.375 | 0.403 |

- No detector wins everywhere; Community-Forensics was the most stable.
- Newest generators are hardest: Flux Dev 21%, Firefly v4 18%, Midjourney v7 24%, Imagen 4 19%, DALL·E 3 31%. Older: ProGAN 87%, StyleGAN2 82%, SD 1.4 73%.
- JPEG compression and resizing were not tested. The paper advises testing on your own data and using an ensemble.
- The paper contradicts itself in places (Community-Forensics mean given as both 75.0% and 78.0%).

## Smaug model card table (self-reported by the authors)

AUC on 26,070 images (OpenFake Reddit, OpenFake Core, CommunityForensics); last column is real photos flagged as AI.

| Model | Reddit | Core | CommFor | Avg | False alarms (Reddit / Core / CF) |
|---|---|---|---|---|---|
| Smaug | 0.973 | 0.991 | 0.981 | 0.982 | 3.0% / 1.4% / 0.4% |
| OpenFake-SwinV2 (non-commercial) | 0.947 | 0.989 | 0.951 | 0.962 | 2.9% / 2.1% / 3.0% |
| Bombek1 | 0.842 | 0.959 | 0.990 | 0.930 | 34.7% / 18.4% / 5.2% |
| Community Forensics 384 | 0.744 | 0.921 | 0.968 | 0.878 | 2.0% / 0.3% / 4.0% |
| Organika/sdxl-detector (non-commercial) | 0.663 | 0.667 | 0.824 | 0.718 | 43.9% / 22.4% / 24.8% |
| umm-maybe/AI-image-detector (no derivatives) | 0.736 | 0.601 | 0.604 | 0.647 | 13.8% / 17.3% / 15.3% |

Smaug at 5% false alarms catches 86.7% (Reddit), 95.8% (Core), 92.2% (CF) of AI images.

## Excluded

| Model | Reason |
|---|---|
| umm-maybe/AI-image-detector | Trained 2022, no recent generators; avg AUC 0.647; CC BY-ND licence |
| Organika/sdxl-detector | SDXL only; avg AUC 0.718; CC BY-NC 3.0 (non-commercial) |
| OpenFake-SwinV2 | CC BY-NC 4.0 (non-commercial); research scripts only |
| B-Free (grip-unina) | Licence bans commercial use; needs Docker and GPU |
| haywoodsloan/ai-image-detector-deploy | No training data documented; about 10% false alarms |
| prithivMLmods/deepfake-detector-model-v1 | Face deepfakes only; experimental |
| ash12321/flux-detector-vit | Flux only |

## Sources

- Ren et al., arXiv 2602.07814: https://arxiv.org/html/2602.07814v1
- Smaug: https://huggingface.co/abacusai/Smaug-AI-Image-Detector
- Community Forensics: https://github.com/JeongsooP/Community-Forensics, https://huggingface.co/OwensLab/commfor-model-384
- Bombek1: https://huggingface.co/Bombek1/ai-image-detector-siglip-dinov2
- OpenFake: https://huggingface.co/datasets/ComplexDataLab/OpenFake
- B-Free: https://github.com/grip-unina/B-Free
