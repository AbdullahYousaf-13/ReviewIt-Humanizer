# Image Detector: API Flow (FE -> BE)

Base URL: `http://127.0.0.1:5000`. Backend: `backend/app.py` (routes), `backend/imagedetector/service.py` (logic). New routes only; existing routes are unchanged. Last updated 2026-11-10.

## Flow

```
PAGE OPENS
FE ── GET  /api/imagedetector/status ──► BE   (repeat every few seconds while state is "loading")
FE ◄─ state: idle | loading | ready ───  BE

CHECK AN IMAGE
FE ── POST /api/imagedetector/detect (file) ──► BE   (about 25 to 33 s; keep the request open)
FE ◄─ label + score + both models ────────────  BE
```

## Where each call is written

| Call | Backend |
|---|---|
| `POST /api/imagedetector/detect` | `backend/app.py` calls `detect_image_service` |
| `GET /api/imagedetector/status` | `backend/app.py` calls `image_status_service` |

## JSON responses

### POST /api/imagedetector/detect
Request: multipart form, field `file` (`.jpg .jpeg .png .webp .bmp .tif .tiff`; `.heic` is not supported). No JSON body, no sign-in (unless switched on, see Settings), no credits. Nothing is saved.

```json
{
  "success": true,
  "filename": "x.jpg",
  "label": "Unclear",
  "band": "unclear",
  "score": -3.07,
  "accuse_cutoff": -1.74,
  "clear_cutoff": -3.16,
  "models": {
    "smaug":   {"probability": 0.0002, "verdict": "Original"},
    "bombek1": {"probability": 0.915,  "verdict": "AI"}
  },
  "seconds": 32.7
}
```

| Key | Meaning |
|---|---|
| `label` | Show this: `AI` (score above `accuse_cutoff`), `Unclear` (above `clear_cutoff`), `Original` (at or below `clear_cutoff`) |
| `band` | Same as `label` for code: `likely_ai`, `unclear`, `likely_real` |
| `score` | Average of the two models' log-odds, 2 decimals |
| `models.*.probability` | Probability the image is AI (0 to 1, 4 decimals) |
| `models.*.verdict` | That model alone: `AI` at probability 0.5 or more, else `Original`. The label does not use it |
| `seconds` | Time the check took on the server |

### Errors (all `{"error": "...", "error_code": "..."}` except where noted)

| Status | `error_code` | When |
|---|---|---|
| 400 | none | No file (`"No image uploaded. Use form field 'file'."`) |
| 400 | `EMPTY_FILE` | File has no bytes |
| 401 | `AUTH_REQUIRED` | Only when `IMAGE_DETECT_REQUIRE_AUTH=1` and not signed in |
| 413 | none | Over `MAX_UPLOAD_MB` (default 25) |
| 415 | `UNSUPPORTED_IMAGE_TYPE` | HEIC/HEIF or another file type |
| 415 | `UNREADABLE_IMAGE` | Not a readable image |
| 429 | `BUSY` | Another image is being checked (one at a time); try again |
| 500 | `DETECTION_FAILED` | Check failed |
| 503 | `IMAGE_PACKAGES_MISSING` | Packages not installed on the server |

### GET /api/imagedetector/status
```json
{
  "success": true,
  "state": "ready",
  "models_ready": true,
  "error": null,
  "require_auth": false,
  "accuse_cutoff": -1.74,
  "clear_cutoff": -3.16
}
```
`state`: `idle` (not loaded yet, loads on the first image), `loading` (about 80 s), `ready`, `failed` (`error` has the reason).

## Notes for the frontend

- A check takes about 30 s on a laptop CPU: show a "checking" state and set no short timeout.
- Send one image at a time; on 429 wait and retry.
- Show `label` as the answer (AI / Unclear / Original). The per-model rows are optional detail.
- CORS: the page's address must be in `CORS_ORIGINS` (default `http://localhost:3000,http://127.0.0.1:3000`).
- The label is a hint, not proof. Tested on photos without people; screenshots and graphics were not tested.

## Settings (backend environment variables)

| Variable | Default | Effect |
|---|---|---|
| `IMAGE_PRELOAD` | 0 | `1` loads both models at start (about 80 s) |
| `IMAGE_DETECT_REQUIRE_AUTH` | 0 | `1` requires sign-in on the detect route (no credit logic) |
| `MAX_CONCURRENT_IMAGE` | 1 | Images checked at once |
| `IMAGE_ACCUSE_CUTOFF` / `IMAGE_CLEAR_CUTOFF` | -1.74 / -3.16 | Band cutoffs |
| `MAX_UPLOAD_MB` | 25 | Upload limit |
| `CORS_ORIGINS` | localhost:3000 | Allowed page addresses |
