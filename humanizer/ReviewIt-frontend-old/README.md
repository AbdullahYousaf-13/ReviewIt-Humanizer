# ReviewIt Humanizer — Frontend

Minimal Next.js UI to test the detect → humanize pipeline. It talks directly to the Flask backend in `../backend`.

## Setup

Requires Node.js + npm (built and tested with Node 26 / npm 11) and the backend running (see `../backend/README.md`).

```bash
cd frontend
npm install
cp .env.example .env.local     # Windows PowerShell: Copy-Item .env.example .env.local
```

`.env.local` holds the backend address (default `http://127.0.0.1:5000`):

```
API_URL=http://127.0.0.1:5000
```

It is read at runtime, so changing it only needs a restart, not a rebuild. (`NEXT_PUBLIC_API_URL` still works as a fallback.)

## Run

```bash
npm run dev
```

Open http://localhost:3000. If you change `.env.local`, restart the server.

## Use

1. **Paste text**, or **Upload file** (`.pdf`, `.docx`, `.doc`, `.txt` — click the box or drag a file onto it), pick a style, click **Detect AI**. Uploaded documents over 20,000 words are cut to the first 20,000 and a banner says so.
2. Sentences flagged as AI are highlighted **red**.
3. **Click a red sentence** — it is rewritten in place (Humarin → T5 → Gemini → Rule-based) and turns **green** (new score below 0.40) or **amber** (rewritten, but still AI-like), with a badge showing which engine won and the new score.
4. **↺ undo** restores the original sentence. The score bar at the top updates as you go.

## Other commands

```bash
npm run lint     # lint
npm run build    # production build
```

Known limitations: see `../OPEN_ISSUES.md`.
