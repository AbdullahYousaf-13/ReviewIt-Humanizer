# Image detector: how to run it

Code: `ReviewIt/backend/imagedetector/` (branch `abdullah/image-detector`, merged to `main`). Two models (Smaug and Bombek1) give one label: AI, Unclear or Original.

## Requirements

| Item | Value |
|---|---|
| Python | 3.12 (the project's `backend/venv`) |
| Memory | About 4 GB of RAM free while both models are loaded |
| Network | First run downloads the models from Hugging Face; later runs can use `HF_HUB_OFFLINE=1` |
| Time | About 26 s per photo on a CPU laptop; first photo adds about a minute of model loading |

## Install (once)

```
cd ReviewIt\backend
venv\Scripts\activate
pip install -r imagedetector\requirements-bombek1.txt
```

This installs the base `requirements.txt` plus the image packages (`transformers==5.20.0`, `sentence-transformers`, `pillow`, `timm`, `peft`).

## Way 1: the API (for the frontend)

| Step | What to do |
|---|---|
| 1. Set | `PowerShell: $env:IMAGE_PRELOAD="1"` (loads both models at start, about 80 s). Optional: `$env:PRELOAD_MODELS="0"` skips the humanizer models |
| 2. Start | `cd ReviewIt\backend`, `venv\Scripts\activate`, `python app.py` (serves on `http://127.0.0.1:5000`) |
| 3. Wait | `GET http://127.0.0.1:5000/api/imagedetector/status` until `state` is `ready` (`idle`, `loading`, `ready`, `failed`) |
| 4. Check an image | `POST http://127.0.0.1:5000/api/imagedetector/detect`, form field `file` (about 25 to 33 s) |

Without `IMAGE_PRELOAD=1` the models stay unloaded at start (`state: idle`). Response format and errors: `IMAGE_API.md`.

## Way 2: the test page (upload one image in a browser)

| Step | What to do |
|---|---|
| 1 | Open the folder `D:\Abd\Programming\image-detector-test-fe\` (plain HTML, not a git repo) |
| 2 | Run `start_backend.bat` and wait about 80 s for the models |
| 3 | Run `start_frontend.bat`, open `http://localhost:8080` |
| 4 | Upload one image: shows the label, combined score, each model's result and the seconds |

Limits: one image at a time (a second request gets 429), no sign-in, no credits, HEIC not supported.

## Way 3: a folder of photos (no server)

| Step | What to do |
|---|---|
| 1. Add photos | Copy them into `ReviewIt\backend\imagedetector\inbox\` (git ignores it) |
| 2. Run | `cd ReviewIt\backend`, `venv\Scripts\activate`, `python -m imagedetector.check_folder` |
| 3. Read | One line per photo: `beach.jpg \| LIKELY REAL \| score -4.21 \| smaug 0.0003 \| bombek1 0.3100 \| 83 s` |
| Optional | `--watch` keeps it running and scores new photos as they arrive (Ctrl+C stops) |

Log file: `imagedetector\logs\detector.log`. A photo is scored again only if it changed (`inbox\.done.json`).

## Labels

| Label | Score |
|---|---|
| LIKELY AI | above -1.74 |
| UNCLEAR | above -3.16, up to -1.74 |
| LIKELY REAL | -3.16 or below |

## Settings (environment variables)

| Variable | Default | Effect |
|---|---|---|
| `IMAGE_PRELOAD` | 0 | `1` loads both models at start |
| `IMAGE_DETECT_REQUIRE_AUTH` | 0 | `1` requires sign-in on the detect route |
| `MAX_CONCURRENT_IMAGE` | 1 | Images checked at once |
| `IMAGE_ACCUSE_CUTOFF` / `IMAGE_CLEAR_CUTOFF` | -1.74 / -3.16 | Label cutoffs |
| `MAX_UPLOAD_MB` | 25 | Upload limit |
| `CORS_ORIGINS` | `http://localhost:3000,http://127.0.0.1:3000` | Allowed page addresses (the test page needs `http://localhost:8080`) |
| `HF_HUB_OFFLINE` | unset | `1` stops network calls once the models are downloaded |

## Problems

| Symptom | Cause / fix |
|---|---|
| `state` stays `loading` for minutes | Low free RAM: close Chrome and other large programs |
| Browser shows a CORS error | Add the page's address to `CORS_ORIGINS` |
| 429 | Another image is being checked; wait and retry |
| First request very slow | Models were not preloaded; set `IMAGE_PRELOAD=1` |
