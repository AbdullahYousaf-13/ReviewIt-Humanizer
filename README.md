# ReviewIt research

Research and experiments for ReviewIt. There are two projects:

| Folder | What it is |
|---|---|
| [humanizer/](humanizer/) | Rewrites AI-flagged sentences so they read as human-written. Holds the scripts, run data and all humanizer and AI-detector docs. See [humanizer/README.md](humanizer/README.md). |
| [image-detection/](image-detection/) | Tells AI-generated images apart from real photos, using open-source models run locally. Docs: [research](image-detection/docs/MODEL_RESEARCH.md), [test plan](image-detection/docs/TEST_PLAN.md), [prompts](image-detection/docs/TEST_PROMPTS.md), [results](image-detection/docs/TEST_RESULTS.md). |

Shared at the root: `.venv/` (one Python environment for both projects), `.env` (API keys, not committed) and `.gitignore`.
