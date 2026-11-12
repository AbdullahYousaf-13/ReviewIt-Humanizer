# Models: one-page reference

Facts checked 2026-11-12. Weights = size of the downloaded file. Licence and parameters from the Hugging Face page. Details and test results are in the research files linked at the bottom.

- **Deployed** = running in the app (code in `ReviewIt/backend/`).
- **Shelved** = tested, not used.

## Deployed

| Model | Job | Hugging Face id | Parameters | Weights | Licence | Code |
|---|---|---|---|---|---|---|
| BERT AI-text detector | Scores each sentence as AI or human | `followsci/bert-ai-text-detector` | 109.5M | 0.44 GB | MIT | `aidetector/pipeline/detector.py` |
| Humarin (T5-base) | Humanizer, first tier | `humarin/chatgpt_paraphraser_on_T5_base` | 222.9M | 0.89 GB | OpenRAIL | `aidetector/pipeline/humarin_humanizer.py` |
| T5 Paraphrase Paws | Humanizer, second tier | `Vamsi/T5_Paraphrase_Paws` | 222.9M | 0.89 GB | Not stated on the model page | `aidetector/pipeline/t5_humanizer.py` |
| Gemini (API) | Humanizer, third tier | `gemini-3.8-flash` (default, env `GEMINI_MODEL`) | n/a (API) | none (no download) | Google API terms | `aidetector/pipeline/humanizer.py`, `gemini_prompt.py` |
| Smaug | Image detector (AI or real) | `abacusai/Smaug-AI-Image-Detector` | 438.8M | 0.88 GB | Apache 2.0 | `imagedetector/detector.py` |
| Bombek1 (SigLIP2 + DINOv2) | Image detector, combined with Smaug | `Bombek1/ai-image-detector-siglip-dinov2` | 740M | 2.11 GB | MIT | `imagedetector/bombek1.py` |

- Humanizer order: Humarin, then T5, then Gemini, then a rule-based fallback (no model).
- Image label = average of Smaug and Bombek1 log-odds (`imagedetector/combined.py`).
- Base models: Humarin and Paws are fine-tuned from `t5-base`; the BERT detector from `bert-base-uncased`; Bombek1 uses SigLIP2-SO400M and DINOv2-Large (both Apache 2.0).
- Humarin is trained on `humarin/chatgpt-paraphrases`. OpenRAIL has use restrictions: check it before commercial use.

## Shelved

| Model | Job | Hugging Face id | Parameters | Weights | Licence | Why shelved |
|---|---|---|---|---|---|---|
| Community Forensics | Image detector | `OwensLab/commfor-model-384` | 21.8M | 0.09 GB | MIT | Caught 5 of 50 AI images at cutoff 0.5 |
| PEGASUS paraphrase | Humanizer | `tuner007/pegasus_paraphrase` | 569M | 2.28 GB | Apache 2.0 | Deletes content (dropped 3 of 4 list items) |
| BART paraphrase | Humanizer | `eugenesiow/bart-paraphrase` | 406M | 1.63 GB | Apache 2.0 | Returns the input almost unchanged |
| BART text simplification | Humanizer | `Nubletz/bart-text-simplification` | 406M | 1.63 GB | Not stated on the model page | Broken: tokenizer and config disagree, output is empty |
| Gemini 3.5 flash-lite, 3.7 flash | Humanizer | same API, other versions | n/a (API) | none | Google API terms | Tested only; 3.8 flash is the default |

- Ruled out without a full test: DIPPER XXL (11B, cannot run on CPU), Styleformer (parked, too informal).
- Image models excluded on licence or scope (umm-maybe, Organika, OpenFake-SwinV2, B-Free and others): see the "Excluded" table in `image-detection/docs/MODEL_RESEARCH.md`.

## Where the details are

| Topic | File |
|---|---|
| Image models: constraints, tests, benchmark | `image-detection/docs/MODEL_RESEARCH.md`, `TEST_RESULTS.md` |
| Humanizer models and candidates | `humanizer/docs/Humanizer-Research-Docs/MODEL_RESEARCH.md` |
| LLM (Gemini) research | `humanizer/docs/Humanizer-Research-Docs/LLM_RESEARCH.md` |
