# Prompt and fallback experiments, 2026-11-02

The scripts behind `docs/ReviewIt-AI-Detector-Docs/RETRY_AND_FALLBACK_EXPERIMENTS_2026-11-02.md`. They use the detector and the fact guard of the ReviewIt backend (`D:\Abd\Programming\ReviewIt\backend`, path set at the top of each script) and **make no Gemini call**: the text they score is hand-written or copied from the logs.

Run each one with the backend's own Python from the backend folder, for example `venv\Scripts\python.exe <path to script>`. The detector is loaded from the local cache and scored on the CPU.

| Script | What it does | Report section |
|---|---|---|
| `move_experiment.py` | 45 hand-written rewrites of 5 failing sentences: split, active/passive, start elsewhere, verb clauses, plainer wording, and combinations; checks the scoring against the logged scores; writes `move_experiment_results.json` | E1 |
| `move_experiment_2.py` | The same sentences: put formal phrases back one at a time, and pad with formal words, to separate length from wording | E1 |
| `s4_factorial.py` | "Emerging leaders…": each of the 4 list items kept or reworded, in a single sentence and in a split frame (32 variants) | E2 |
| `retention.py` | Do passing rewrites keep fewer of the original's content words than failing ones? (27 full-text rewrites from the live runs) | E3 |
| `candidates.py` | Pass rate per candidate by call, shape, length and sentence (data copied from the `[humanizer-diag]` logs of two live runs) | Live results |
| `connectives.py` | A final "too" / "as well" or a leading "In this way," / "Overall," / "Also," on 5 rewrites that scored 97–100% | E4 |
| `connectives_all.py` | The same on the 16 original sentences, with the fact guard | E4 |
| `guard_check.py` | Does the fact guard accept the connective variants? | E5 |
| `fallback_e2e.py` | The connective fallback end to end with the real detector and guard and a mocked Gemini | E6 |
