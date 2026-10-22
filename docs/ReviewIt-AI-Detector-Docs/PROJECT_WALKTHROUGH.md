# Project walkthrough — branch `abdullah/humanizer-dev`

This note covers only the work on this branch. The original project (the detector, the first humanizer and the Flask API) was already there and is described only as the starting point.

---

## 1. The project in one minute

**What the app does.** You paste text or upload a document. The app finds the sentences that look AI-written and highlights them in red. You click a red sentence and the app rewrites it so a detector scores it lower. You can undo the rewrite or compare the original and the rewrite side by side.

**If someone asks "what did you do?"**

> The backend already had a detector and a humanizer. I made **Humarin the first rewriter**, with Humarin → T5 → Gemini → Rule-based as fallbacks, and made the API tell the page which rewriter won. I built a **Next.js test frontend**: paste or upload, red AI sentences, click to rewrite in place, undo, and a side-by-side Compare view. I measured why rewriting was slow and found it is mostly the **Gemini free-tier key**, not the models. I fixed several backend bugs on the way (hyphens lost in uploads, fake default scores, missing requirements, a dead Gemini model) and wrote READMEs and a list of open issues. Rewriting a whole document in one click is left out until I talk to my supervisor.

**Size of the work:** 40 files changed compared to `main`. About 6,900 of the 9,000 added lines are `package-lock.json`, so the real code and docs are around 2,100 lines.

---

## 2. What changed on this branch

**Before:** Gemini was tried first. If it failed, T5 and then a rule-based rewriter were used. A local detector (BERT) scored every rewrite and the lowest score won.

**Now:** Humarin first, then T5, then Gemini, then rule-based. The API also returns the name of the winner. A frontend exists.

| Date | Commits | What |
|---|---|---|
| 13–14 Oct | `0d9384f`, `3d55e2a` (yours, before this session) | Humarin module and test scripts; Humarin added to the main pipeline; fallback order changed; `engine` added to the response |
| 14 Oct | 18 commits `d17689a` … `1945ec3` | Frontend, backend fixes, docs |

---

## 3. AI / ML side

### 3.1 How one rewrite is chosen
1. The detector scores the original sentence (0 = human, 1 = AI).
2. Humarin writes 5 versions. Each is scored. The lowest score so far is kept.
3. If the best score is still **0.40 or more**, T5 writes up to 3 versions. Same scoring.
4. If it is still 0.40 or more, Gemini writes 3 versions. If it is still 0.35 or more, Gemini is asked for 3 simpler ones.
5. If nothing has improved the sentence, or the best is still 0.50 or more, the rule-based rewriter runs.
6. The winner is cleaned up and returned with its score and its name (`engine`).

The numbers to remember: **0.75** = the detector calls it AI. **0.40** = our "good enough" line. **0.50** = when the rule-based rewriter is used. **0.35** = when Gemini gets a second try.

### 3.2 Decisions

**Humarin is the first rewriter** *(you and your supervisor)*
- *Why:* it runs on your own computer. No API key, no quota, no cost, no internet needed.
- *Other options:* keep Gemini first (the original design); T5 only; PEGASUS or BART (your research: PEGASUS deleted content and BART just copied the input).
- *Know this:* in your 20-set test, Gemini passed both detectors on 12 of 20 sets and Humarin on 8 of 20. Humarin also dropped two statistics. Gemini kept every statistic but repeated citations. So Humarin first is a choice for local and free, not because it is stronger.
- *Check with your supervisor* what exactly their reason was. It is not written anywhere.

**Every rewrite is checked by the same detector** *(original design, kept)*
- *Why:* the detector score is the goal, so every candidate is measured with it and the lowest wins.
- *Limit:* the score says "looks like AI". It does not check that facts, numbers or citations survived.

**Gemini uses one model only, `gemini-3.8-flash`** *(your decision)*
- *Why:* the old code tried five model names one after another. One of them returned "not found" and the others often returned "overloaded". Each failure cost 5 to 9 seconds.
- *Other options:* keep the list; add a time limit; use a paid key.
- If Gemini fails, the code moves on to the next rewriter.

**Gemini writes 3 versions (it was 4)** *(your decision)*
- *Why:* 3 versions for both Gemini and T5, fewer tokens.
- *Not checked live:* the free-tier quota ran out right before. It is a two-line change in the prompt, but we did not see a real answer with exactly 3.

**T5: every version it writes is scored** *(you approved)*
- *Why:* T5 wrote 3 versions but only the first different one was scored.
- *How:* a new function `paraphrase_candidates()`. The old `paraphrase_sentence()` behaves exactly as before, because other code uses it. We tested both on 5 inputs and got identical results.
- *Honest note:* often only 1 or 2 of T5's 3 versions differ from the original, so the gain is small.

**Ideas we tested and dropped**
- *"Make T5 return only 1 version."* Measured: 3 versions take 5.2 s and 1 version takes 5.2 s. The time goes into the search, not into the number returned. So nothing is saved.
- *"Write one version at a time and stop when one is good."* Measured on 6 sentences: the first Humarin version scored under 0.40 in **0** of 6. One-at-a-time writing costs about 2.7 s per version, so it would be slower than one batch of 5 (about 5.4 s).
- *What would really speed things up:* a GPU, or a cheaper search. That is your supervisor's decision.

**Green and amber at 0.40** *(you approved)*
- A rewrite is **humanized (green)** only if its own score is below 0.40. If the text changed but the score is 0.40 or more, it is **attempted (amber)**.
- *Why 0.40:* it is the pipeline's own "good enough" line.
- *Other options:* 0.75 (the detector's AI line); count any improvement as success (a drop from 1.00 to 0.99 would look like a win).

**Style only changes Gemini** *(finding)*
- The style picks a sentence in the Gemini prompt. Humarin ignores it, and T5 accepted it but never used it. We removed the unused style argument from the new T5 function.

### 3.3 Numbers you can quote

| Measurement | Result |
|---|---|
| One click, 32-word sentence, local rewriters only | about **12 s** (Humarin 5 s + T5 5.6 s + scoring 1.1 s) |
| A 15-word sentence | about 2 s per rewriter |
| Humarin settings | 5 versions: 5.4 s · 1 version: 5.3 s · greedy (1 version, no search): 2.5 s |
| Gemini on this key | "overloaded" errors on a trivial prompt; one call took **188 s**; then "quota exceeded, limit 20" |
| Group score example | 1.0 → one rewrite 0.9999 → two rewrites **0.1654** |
| Three clicks at once | all finished after about 26 s (one alone: 17.6 s) |
| Computer | i5-8250U laptop, 4 cores, no GPU |

### 3.4 Limits to mention
- Scores come from **one** detector (the local BERT model), not from ZeroGPT or Copyleaks.
- The pipeline does not check that facts, numbers and citations are preserved.
- With the Gemini free quota used up, rewriting runs on Humarin, T5 and rule-based only.

---

## 4. Backend

**Already there:** a Flask server (`backend/app.py`) with the logic in `backend/aidetector/service.py`. Uploads become background jobs kept in memory.

### 4.1 Decisions

**Use the existing API, no new endpoints** *(your decision)*
- The frontend uses five existing calls, plus `/api/detector-score`, which nobody used before.
- *Other options:* add batch or whole-document endpoints; switch to FastAPI; add a proxy.

**The response includes `engine`** *(yours, before this session)*
- The page needs to show which rewriter won.

**Humarin has its own loader inside `humanizer.py`** *(yours)*
- A separate file, `humarin_humanizer.py`, is used only by `test_humarin.py`. The pipeline has its own copy of the loader. The reason for two copies is not written anywhere, so do not make one up.

**Keep the hyphen when joining words split at a line end** *(you approved)*
- *Problem:* `well-` at the end of a line plus `differentiated` on the next line became `welldifferentiated`. Only uploads were affected.
- *Fix:* a one-character change in a regular expression.
- *Other options:* join only when the result is a real word (needs a word list); leave it.
- *Trade-off:* a word that was only split by the line wrap (`inter-` + `national`) keeps a stray hyphen. That is less harmful than a merged non-word.

**No invented scores** *(you approved)*
- *Problem:* if the humanizer left out its scores, the service filled in 0.85, 0.15 and 0.70.
- *Fix:* a missing score now produces a clear error.

**Requirements completed** *(you approved)*
- Added `flask==3.1.3`, `flask-cors==6.0.5` and `google-genai==2.30.0` to `aidetector/requirements.txt`. They were already installed but not listed.

**Housekeeping:** an out-of-date comment in `humanizer.py` was fixed, and `backend/README.md` was added.

### 4.2 Left alone on purpose

| Item | Why |
|---|---|
| Time limit on Gemini calls | Supervisor's pipeline; a paid key probably removes the need |
| A "document was cut" flag and an upload size limit | You chose to leave the backend alone; the page shows a banner instead |
| `debug=True`, open to the network, open CORS, fixed `secret_key` | Fine on a laptop. Only matters when deployed. The key is not even used |
| Three API implementations (Flask and two FastAPI files, one of which cannot start) | Needs the supervisor's decision on what to delete |
| 9 styles listed but 6 accepted | Supervisor's decision |
| Several clicks at once (no queue, models load without a lock) | Logged; not seen as a bug |
| Whole-document rewrite (`/api/humanize`) | Out of scope for now |

### 4.3 Problems we solved
- **Windows Smart App Control** blocked a PyTorch file (`WinError 4551`), so the backend could not start. You turned Smart App Control off. The other options were WSL2, another machine, or a different PyTorch build.
- **Free Gemini key:** the quota is 20 requests a day. The fix is a paid key set as `GOOGLE_API_KEY_PAID`. The code already prefers that key.

---

## 5. Frontend

**Built with:** Next.js 16.4, React 19, TypeScript, Tailwind CSS. It lives in `frontend/`, next to `backend/`.

### 5.1 Decisions

**Only the original workflow** *(your decision)*
- Detect, highlight, click a sentence, rewrite in place, undo. You turned down extras such as a separate "quick humanizer" tab.

**The page calls the backend directly, with the address read at runtime** *(you approved)*
- *Why:* rewriting can take minutes. A Next.js proxy would give up earlier (I believe about 30 s; not checked). The server already allows CORS.
- *How:* `page.tsx` reads `API_URL` each time the page is served. Changing it needs a restart, not a rebuild. We proved it with one build and two servers.
- *Other options:* a build-time variable; a proxy.

**Paste text or upload a file** *(the original backend supports both)*
- Upload is a job: send the file, ask every 1.5 s until it is done, fetch the result, then delete the job on the server.

**Click a red sentence to rewrite it in place** *(the original workflow)*
- The page also sends the sentences before and after, as background for the rewrite. Those are the sentences as shown at that moment.

**Colours:** red = AI, green = humanized, amber = rewritten but still AI-like, grey = no better rewrite, blue = working.

**Group scores for the headline numbers** *(you asked for this)*
- *Problem:* "AI score now" mixed group scores (for untouched sentences) with single-sentence scores (for rewritten ones).
- *Fix:* after every rewrite or undo, the page scores the changed group of four again with `/api/detector-score` and averages group scores. The badge on a sentence keeps its own score, as you wanted.
- *Other options:* leave the mix; run a whole new detection; show only per-sentence scores.
- The group size (4) is written in two places: `Studio.tsx` and `detector.py`. They must match.

**Highlight | Compare switch** *(your supervisor's request, your design)*
- Compare shows original on the left and rewrite on the right, row by row, with a "Show only changed sentences" checkbox. It becomes available after the first rewrite. No per-row scores.
- *Other options:* a pop-up window; two flowing paragraphs; word-level differences.

**Amber "attempted"** *(you approved)*
- Counted separately from "humanized". Still counted as "flagged as AI". Shown in Compare.

**Style dropdown** *(you approved)*
- A fixed list of the 6 styles that work. The backend lists 9, but three silently behave like "academic". The select is a rounded pill with a chevron, like the View switch.

**Smaller things:** a timer while a sentence is being rewritten; the browser-extension warning silenced; the "Backend connected" pill removed; drag-and-drop upload; an amber banner when an upload was cut to 20,000 words.

### 5.2 Left out on purpose
A "rewrite the whole document" button (waiting for your supervisor), an upload size limit, a queue for many clicks at once, a tooltip saying style only affects Gemini, a custom dropdown menu.

### 5.3 How it was checked
- Every change: type check, lint and a production build.
- Real calls to the server for health, CORS, detect, upload (`.txt`, `.docx`, `.pdf`), rewrite and group scoring.
- Your screenshots showed detect, rewrite, undo and Compare working in the browser.
- **Not seen in a browser yet:** the amber state, the pill select, drag-and-drop and the truncation banner. Gemini returning exactly 3 versions was not seen either.

---

## 6. Code decisions (the "how")

**Backend**
1. `_generate_candidates()` returns `None` when nothing was tried or it failed, and `[]` when the model produced nothing usable. That way `paraphrase_sentence()` returns exactly what it always did.
2. A new function `paraphrase_candidates()` was added instead of changing `paraphrase_sentence()`, because other code calls the old one.
3. `_call_gemini` logs the error and raises it again. The existing error handling then moves to the next rewriter.
4. The service raises an error for missing scores inside its existing error handling, so the page gets the same kind of error message as before.
5. The test and timing scripts were kept out of the repository. The results are in `OPEN_ISSUES.md` and here.

**Frontend**
1. All state lives in one component, `Studio.tsx`. A state library would be too much for an app this small.
2. `createApi(baseUrl)` is a function that builds the API helper, so the address can be a runtime value.
3. One helper, `request()`, handles every call and turns failures into readable messages.
4. Three guards against late replies: an `AbortController` (cancel), a `runId` counter (ignore rewrites that finish after a new detection) and `scoredTexts` (ignore group scores for text that changed again).
5. Group scores are re-checked by a watcher that compares each block's text with the text last scored. That covers both rewrite and undo. It never calls `setState` directly inside the watcher, because this project's lint rules reject that (we tested it).
6. Numbers like "AI score now" and the counts are calculated each time the page draws, not stored.
7. Constants are in `lib/config.ts` (`STYLES`, `MAX_ANALYSED_WORDS`) or next to the code that uses them (`HUMAN_THRESHOLD`, `BLOCK_SIZE`), with comments naming the backend value they must match.
8. The page is split into small components: `InputCard`, `SentenceView`, `CompareView`, `ViewToggle`, `ScoreSummary`, `EngineBadge`, `Navbar`.
9. `page.tsx` is a server component that reads the address after `await connection()` inside `<Suspense>`. The scaffold turns on a setting (`cacheComponents`) that requires this.
10. The View switch is a radio group with `aria-checked`. The style control stays a real `<select>` with `appearance-none` and an icon.

---

## 7. Your contribution

**What you did**
- Set the goal: a minimal ReviewIt-style Next.js frontend for the **original** pipeline only.
- Described the workflow and brought in your supervisor's requests: the Compare view, Gemini 3.8 as the default, the paid key.
- Made the decisions listed above: whole-document rewrite deferred; Gemini one model and 3 variants; Humarin stays at 5; T5 left as is; early-exit idea dropped; block-wise scores; amber state; keep the hyphen; leave the backend size limit; runtime address; style list; Compare design.
- Tested in the browser and reported the problems that led to fixes: the console error, the slow rewrite, `welldifferentiated`, the `Tier 4 · 1.00` result, the 10-second Humarin question, the several-clicks question.
- Turned off Smart App Control, started the servers yourself, and set the working rules: plan before building, check before claiming, push only to `abdullah/humanizer-dev`, no AI tag on new commits.

**How the code was made**
- Everything is committed under your name. This session's code was written with Claude Code as the coding assistant. The 18 commits from this session carry a `Co-Authored-By` tag; new commits do not.
- Your two earlier commits are yours. Say how you made them the way it really happened.

**A suggested answer**
> I set the requirements and made the design decisions: what to build and leave out, the thresholds, how scores are shown and how the fallbacks work. I tested it in the browser and reported the bugs that shaped the fixes. I integrated Humarin earlier. For the frontend and the backend fixes I worked with Claude Code as my coding assistant.

Be ready to explain in your own words: the four rewriters and their order, why scores are per group of four, green versus amber, why a click takes about 12 s, and the Gemini free-tier limit.

---

## 8. Stack and libraries

**Frontend**

| Tool | Version | Used for |
|---|---|---|
| Next.js (App Router) | 16.4.0 | The whole app |
| React | 19.3.0 | Components and state |
| TypeScript | 5.9.3 | Types for the server's replies |
| Tailwind CSS | 4.3.3 | All styling |
| ESLint | 9.39.5 | Checking code on every change |
| Geist fonts | — | Page fonts (scaffold default) |
| `fetch` and `AbortController` | built in | All server calls and cancelling |

No state library, no UI kit, no axios.

**Backend** (already there; nothing new installed)

| Tool | Version | Used for |
|---|---|---|
| Python | 3.12.10 | Runtime |
| Flask, flask-cors | 3.1.3, 6.0.5 | The server and browser access |
| PyTorch (CPU) | 2.14.1 | Runs the local models |
| transformers | 5.19.0 | Loads BERT, Humarin and T5 |
| NLTK | 3.9.1 | Cutting text into sentences |
| PyMuPDF | 1.28.2 | Reading PDFs |
| python-docx | 1.2.0 | Reading Word files |
| python-dotenv | 1.0.0 | Reading `backend/.env` |
| google-genai | 2.30.0 | Talking to Gemini |

**Models**

| Model | Role | Chosen by |
|---|---|---|
| `followsci/bert-ai-text-detector` | Scores AI-ness; flags at 0.75 | Original code |
| `humarin/chatgpt_paraphraser_on_T5_base` | Rewriter 1 | You and your supervisor |
| `Vamsi/T5_Paraphrase_Paws` | Rewriter 2 | Original code |
| `gemini-3.8-flash` | Rewriter 3 | Your supervisor's default |
| Rule-based code | Rewriter 4 | Original code |

---

## 9. Files we changed

**Frontend (`frontend/`, about 1,050 lines of source, all new)**
`src/app/layout.tsx`, `page.tsx`, `globals.css` · `src/lib/api.ts`, `types.ts`, `config.ts` · `src/components/Studio.tsx` (state and logic), `InputCard.tsx`, `SentenceView.tsx`, `CompareView.tsx`, `ViewToggle.tsx`, `ScoreSummary.tsx`, `EngineBadge.tsx`, `Navbar.tsx` · `.env.example`, `README.md`, plus files generated by `create-next-app`.

**Backend (`backend/`)**
- `aidetector/pipeline/humarin_humanizer.py`, `test_humarin.py`, `test_gemini.py` — yours, before this session.
- `aidetector/pipeline/humanizer.py` — Humarin tier and new order (yours); one Gemini model, 3 variants, T5 loop, comment fix (this session).
- `aidetector/pipeline/t5_humanizer.py` — `paraphrase_candidates()`.
- `aidetector/service.py` — `engine` in the response (yours); no invented scores (this session).
- `app.py` — `engine` copied into the response (yours).
- `aidetector/pipeline/pdf_extractor.py` — keep the hyphen.
- `aidetector/requirements.txt`, `README.md`.

**Docs:** `OPEN_ISSUES.md` (open issues only), the two READMEs, and these private notes.

---

## 10. Questions you may get

1. **Why Humarin first?** It runs locally and is free: no key, no quota, no internet. Gemini scored better in my 20-set test (12 of 20 against 8 of 20) and keeps facts better, so it stays as a fallback.
2. **Why is rewriting slow?** The local rewriters take about 5 to 12 s on this laptop. The long waits came from the Gemini free-tier key: overloaded errors, one 188 s call, then a 20-requests-a-day limit. A paid key and a GPU would fix it.
3. **How is the AI score worked out?** A detector scores groups of 4 sentences, and each sentence shows its group's score. After a rewrite, the page scores the group again, so the top number stays comparable.
4. **What do green and amber mean?** Green: the rewrite scores below 0.40. Amber: the text changed but still looks AI.
5. **What does the Style dropdown do?** It only changes Gemini's instructions. Humarin and T5 ignore it.
6. **Why does the page call the backend directly?** Rewrites are slow and CORS is already on. The address is now read at runtime.
7. **What did you fix in the backend?** Lost hyphens in uploads, invented scores, missing requirements, a dead Gemini model and an out-of-date comment.
8. **What did you leave out, and why?** Whole-document rewrite, a Gemini time limit, an upload size limit and merging the three APIs. Those are scope or supervisor decisions. All are in `OPEN_ISSUES.md`.
9. **Does it keep citations and facts?** The pipeline only lowers the detector score. It does not check facts. In my research, both models can drift: Humarin dropped two statistics and Gemini repeated citations.
10. **What next?** Get the paid key and measure again; decide what to do about the three APIs; add a time limit for Gemini; consider a fact-check; maybe use a GPU.

---

## 11. Words used here

- **Rewriter / engine:** one of Humarin, T5, Gemini or rule-based.
- **Block:** four sentences in a row that the detector scores together.
- **Detector:** the BERT model that gives a 0-to-1 AI score.
- **Humarin:** a paraphrasing model (`humarin/chatgpt_paraphraser_on_T5_base`).
- **Attempted:** rewritten, but the new score is still 0.40 or more.
- **API call:** a message from the page to the server, sent to an address like `/api/detect-text`.
- **Job:** an upload being processed in the background, with its own id.
