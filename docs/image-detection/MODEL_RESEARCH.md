# AI-generated image detection: model research

Date: 3 Nov 2026
Code branch: `abdullah/image-detector` (ReviewIt repo, from `main`)
Scope: open-source models that run locally. Paid APIs are out of scope.

## 1. Short answer

Yes, open-source models can tell AI images from real ones, but no single model is reliable on every generator. The newest commercial generators (Flux, Midjourney 7, Imagen 4, Firefly, GPT-image, Nano Banana) are the hardest cases.

**Shortlist to test on our own images:**

| Rank | Model | Why | Licence |
|---|---|---|---|
| 1 | `abacusai/Smaug-AI-Image-Detector` | Best published scores on the newest generators, low false alarms, runs on CPU | Apache 2.0 |
| 2 | `OwensLab/commfor-model-384` (Community Forensics) | Most consistent model in an independent 2026 benchmark; very small (21.8M params) | MIT (code and weights) |
| 3 | `Bombek1/ai-image-detector-siglip-dinov2` | Strong on DALL·E 3 and Midjourney v6, but flags too many real photos | MIT |

**Do not use:** `umm-maybe/AI-image-detector` and `Organika/sdxl-detector`. They are the most downloaded, but they are old (2022–2023) and scored worst in the comparison (see section 3).

**Recommended next step:** build a small test set of our own (real photos plus images from current generators) and run the 3 shortlisted models on it before choosing. Every source below says lab numbers do not carry over to new data.

## 2. Independent benchmark (most trustworthy source)

*"How well are open sourced AI-generated image detection models out-of-the-box"*, Ren et al., arXiv 2602.07814, Feb 2026. They tested 16 methods on 12 datasets (about 2.6M images, 291 generators).

Mean accuracy (Table 3, top and bottom):

| Detector | Mean | Median |
|---|---|---|
| Community-Forensics | 0.780 | 0.821 |
| SAFE | 0.688 | 0.812 |
| PatchCraft | 0.675 | 0.742 |
| DRCT CLIP-ViT (SD v2.0) | 0.718 | 0.696 |
| ... | | |
| UnivFD | 0.407 | 0.497 |
| CNNSpot | 0.375 | 0.403 |

Main findings:
- No detector wins everywhere; rankings change a lot from dataset to dataset. Community-Forensics was the most stable.
- Accuracy is far lower on new generators: Flux Dev 21%, Firefly v4 18%, Midjourney v7 24%, Imagen 4 19%, DALL·E 3 31%. Older ones score much higher: ProGAN 87%, StyleGAN2 82%, SD 1.4 73%.
- Even Community-Forensics got only 35–42% on the newest commercial generators.
- The paper did not test JPEG compression or resizing.
- The paper's advice: test on your own target data, and use an ensemble where possible.

Caveats: the paper contradicts itself in places (Community-Forensics' mean is given as 75.0% in one place and 78.0% in another, and the number of detectors varies). Smaug was not part of this benchmark.

## 3. Head-to-head table from the Smaug model card

Source: the `abacusai/Smaug-AI-Image-Detector` model card. **The model's own authors ran this**, so treat it as self-reported. All models were scored on the same 26,070 test images (OpenFake Reddit, OpenFake Core, CommunityForensics). Metric: AUC, where 1.0 is perfect and 0.5 is a coin flip.

| Model | Reddit | Core | CommFor | Avg | Real photos flagged as AI (Reddit / Core / CF) |
|---|---|---|---|---|---|
| Smaug-AI-Image-Detector | 0.973 | 0.991 | 0.981 | **0.982** | 3.0% / 1.4% / 0.4% |
| OpenFake-SwinV2 | 0.947 | 0.989 | 0.951 | 0.962 | 2.9% / 2.1% / 3.0% |
| s-gehring/detectra-openfake | 0.936 | 0.972 | 0.954 | 0.954 | 2.7% / 1.2% / 2.0% |
| Thermostatic-Frontier | 0.894 | 0.977 | 0.979 | 0.950 | 16.4% / 6.6% / 17.7% |
| Bombek1-SigLIP-DINOv2 | 0.842 | 0.959 | 0.990 | 0.930 | 34.7% / 18.4% / 5.2% |
| haywoodsloan-SwinV2 | 0.897 | 0.953 | 0.901 | 0.917 | 9.5% / 1.1% / 10.6% |
| TensorFold/detectra-v1 | 0.748 | 0.933 | 0.965 | 0.882 | 5.3% / 0.6% / 3.5% |
| CommFor-384 (OwensLab) | 0.744 | 0.921 | 0.968 | 0.878 | 2.0% / 0.3% / 4.0% |
| Ateeqq/ai-vs-human-image-detector | 0.867 | 0.905 | 0.694 | 0.822 | 27.2% / 14.3% / 40.1% |
| Organika/sdxl-detector | 0.663 | 0.667 | 0.824 | 0.718 | 43.9% / 22.4% / 24.8% |
| umm-maybe/AI-image-detector | 0.736 | 0.601 | 0.604 | 0.647 | 13.8% / 17.3% / 15.3% |

At 5% false alarms, Smaug catches 86.7% (Reddit), 95.8% (Core) and 92.2% (CF) of AI images.

## 4. Model details

### 4.1 abacusai/Smaug-AI-Image-Detector (rank 1)
- Architecture: EmbeddingGemma-2 image encoder with a linear classifier; 439M params; bf16.
- Licence: Apache 2.0 (commercial use is allowed).
- Generators covered, as the card lists them: GPT-Image 2, Nano Banana Pro, Midjourney 7, Seedream 5, FLUX.2, Z-Image, Recraft, Ideogram, ERNIE-Image, Sora 2 and Veo 3 frames, DALL·E 3, Firefly 3. There is no per-generator breakdown.
- Robustness: trained on resized, recompressed and blurred images, with professional photos used as hard negatives.
- Runs on: NVIDIA GPU (~1 GB), Apple Silicon or CPU. It needs custom code (`smaug_image_detect`, from `sentence-transformers[image]`), not a plain transformers pipeline. Output is a score from 0 to 1, with 0.5 as the default threshold. A `crops=1` mode is 3x faster.
- Downloads last month: 7,763.
- Limitations given on the card: brand-new or evasion-tuned generators may get through; real photos with a small AI-edited region may be scored as real; the score is evidence, not proof.

### 4.2 OwensLab/commfor-model-384, Community Forensics (rank 2)
- Paper: Park & Owens, CVPR 2025. Trained on 2.7M images from 4,803 generators.
- Size: 21.8M params (ViT, small). There is also a 224 px variant (`commfor-model-224`).
- Licence: MIT for code and weights. The dataset licence is unclear (there is an open "licensing question" discussion on Hugging Face). We only need the weights.
- Weights updated 28 Aug 2025.
- It was the most consistent detector in the independent benchmark, but it is weaker on Reddit-style real-world images (AUC 0.744 in the Smaug table). Its false-alarm rate is low.
- The card does not state CPU support, but a model this small should run on CPU (to be verified).

### 4.3 Bombek1/ai-image-detector-siglip-dinov2 (rank 3)
- Ensemble of SigLIP2-SO400M and DINOv2-Large (LoRA); ~740M params. MIT licence.
- Trained on OpenFake (~95K images), with JPEG, blur, noise and resize augmentation.
- Self-reported accuracy: DALL·E 3 100%, Midjourney v6 96.33%, AI-or-Not 96.80%.
- Weakness: **many false alarms on real photos.** The card itself reports ~9% on COCO-style photos, and the Smaug table measured 34.7% on Reddit. It performs poorly below 128×128 px and on screenshots or graphics.
- Needs custom code (`model.py`).

### 4.4 Rejected or excluded
| Model | Reason |
|---|---|
| umm-maybe/AI-image-detector | Trained in Oct 2022 with no Midjourney 5, SDXL or DALL·E 3 images; built for artwork; avg AUC 0.647; CC BY-ND licence |
| Organika/sdxl-detector | SDXL only; avg AUC 0.718; 43.9% false alarms on Reddit; **non-commercial** (CC BY-NC 3.0) |
| haywoodsloan/ai-image-detector-deploy | Apache 2.0 and runs in a transformers pipeline, but no training data is documented and false alarms are around 10% |
| OpenFake-SwinV2 (vicliv/OpenFake) | Scores well (#2), but weights are **CC BY-NC 4.0 (non-commercial)**, hosted on Google Drive, and only usable through research scripts |
| B-Free (grip-unina, CVPR 2025) | Strong robustness claims, but the licence **bans commercial use**, it has no batch support, and it is set up for Docker with a GPU |
| prithivMLmods/deepfake-detector-model-v1 | Targets face deepfakes; small private dataset; marked "experimental" |
| ash12321/flux-detector-vit | Detects Flux only; labels everything else as "Real" |

## 5. Open questions for the supervisor

1. **Commercial use:** will ReviewIt be a commercial product? If so, only Apache 2.0 or MIT models are allowed (Smaug, Community Forensics, Bombek1). That rules out B-Free, OpenFake and Organika.
2. **Hardware:** where will this run, on a CPU-only server or with a GPU? Smaug and Community Forensics both work on CPU.
3. **Single model or ensemble:** the benchmark recommends an ensemble (for example Smaug + Community Forensics), which costs more compute.
4. **Image types:** photos only, or artwork, screenshots and partly AI-edited images too? All the models are weaker on those.

## 6. Sources
- Ren et al., *How well are open sourced AI-generated image detection models out-of-the-box*, arXiv 2602.07814: https://arxiv.org/html/2602.07814v1
- Smaug model card: https://huggingface.co/abacusai/Smaug-AI-Image-Detector
- Bombek1 model card: https://huggingface.co/Bombek1/ai-image-detector-siglip-dinov2
- Community Forensics: https://jespark.net/projects/2024/community_forensics/, https://github.com/JeongsooP/Community-Forensics, https://huggingface.co/OwensLab/commfor-model-384
- B-Free: https://grip-unina.github.io/B-Free/, https://github.com/grip-unina/B-Free
- OpenFake: https://github.com/vicliv/OpenFake, https://huggingface.co/datasets/ComplexDataLab/OpenFake
- https://huggingface.co/umm-maybe/AI-image-detector
- https://huggingface.co/Organika/sdxl-detector
- https://huggingface.co/haywoodsloan/ai-image-detector-deploy
- https://huggingface.co/prithivMLmods/deepfake-detector-model-v1
- https://huggingface.co/ash12321/flux-detector-vit

Nothing here has been run locally yet. All numbers come from the papers and model cards listed above.
