"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import { ApiError, createApi } from "@/lib/api";
import { DEFAULT_STYLE, MAX_ANALYSED_WORDS, MAX_CONCURRENT_HUMANIZE } from "@/lib/config";
import type { DetectedHeading, DetectionResult } from "@/lib/types";
import CompareView from "./CompareView";
import InputCard from "./InputCard";
import ScoreSummary from "./ScoreSummary";
import SentenceView, { type ViewSentence } from "./SentenceView";
import ViewToggle, { type View } from "./ViewToggle";

// A rewrite counts as "humanized" only if its own score is below this bar (the pipeline's pass mark:
// humanizer.py labels a sentence "ai" at >= 0.40). Anything else that changed is "attempted".
const HUMAN_THRESHOLD = 0.4;

// The detector scores sentences in fixed blocks of 4 and gives each sentence its block's score
// (_group_into_paragraphs(size=4) in backend/aidetector/pipeline/detector.py). Keep in sync.
const BLOCK_SIZE = 4;
const blockText = (list: ViewSentence[], block: number) =>
  list
    .slice(block * BLOCK_SIZE, (block + 1) * BLOCK_SIZE)
    .map((s) => s.text)
    .join(" ");

type Busy = null | "detecting" | "uploading" | "processing";

const BUSY_LABEL: Record<Exclude<Busy, null>, string> = {
  detecting: "Detecting…",
  uploading: "Uploading…",
  processing: "Processing document…",
};

const isAbort = (e: unknown) => e instanceof DOMException && e.name === "AbortError";
const message = (e: unknown) => (e instanceof Error ? e.message : "Something went wrong.");

export default function Studio({ apiUrl }: { apiUrl: string }) {
  const api = useMemo(() => createApi(apiUrl), [apiUrl]);
  const [style, setStyle] = useState<string>(DEFAULT_STYLE);
  const [busy, setBusy] = useState<Busy>(null);
  const [error, setError] = useState<string | null>(null);
  const [sentences, setSentences] = useState<ViewSentence[]>([]);
  const [initialScore, setInitialScore] = useState(0);
  const [view, setView] = useState<View>("highlight");
  const [blockScores, setBlockScores] = useState<number[]>([]);
  const [scoreWarning, setScoreWarning] = useState(false);
  const [truncated, setTruncated] = useState(false);
  const [notes, setNotes] = useState<string[]>([]);
  const [softError, setSoftError] = useState(false); // the file is not supported: amber notice instead of a red error
  const [headings, setHeadings] = useState<DetectedHeading[]>([]);
  const [modelsReady, setModelsReady] = useState(true); // false only while the backend reports it is still loading

  const controller = useRef<AbortController | null>(null);
  const runId = useRef(0); // invalidates in-flight humanize calls when a new detection starts
  const scoredTexts = useRef<string[]>([]); // block text each entry of blockScores was computed for

  useEffect(() => () => controller.current?.abort(), []);

  // The detector / Humarin / T5 models load when the backend starts; tell the person while that is still going on.
  useEffect(() => {
    const ctl = new AbortController();
    let timer: ReturnType<typeof setTimeout> | undefined;
    const check = async () => {
      try {
        const health = await api.getHealth(ctl.signal);
        if (health.models_ready === false) {
          setModelsReady(false);
          timer = setTimeout(check, 2000);
        } else {
          setModelsReady(true);
        }
      } catch {
        if (!ctl.signal.aborted) timer = setTimeout(check, 3000); // backend not up yet: keep trying quietly
      }
    };
    void check();
    return () => {
      ctl.abort();
      if (timer) clearTimeout(timer);
    };
  }, [api]);

  // Humanize requests: a small queue instead of firing every click at once (see pump()).
  const sentencesRef = useRef<ViewSentence[]>([]); // always the latest sentences, updated together with the state
  const update = (fn: (prev: ViewSentence[]) => ViewSentence[]) => {
    sentencesRef.current = fn(sentencesRef.current);
    setSentences(fn);
  };
  const replaceAll = (list: ViewSentence[]) => {
    sentencesRef.current = list;
    setSentences(list);
  };
  const queue = useRef<number[]>([]); // ids waiting for a free slot, in click order
  const running = useRef<Set<number>>(new Set()); // ids whose request is in flight

  // Re-score a block whenever its text changes (humanize / undo), the way the detector scored it.
  useEffect(() => {
    const myRun = runId.current;
    for (let b = 0; b * BLOCK_SIZE < sentences.length; b++) {
      const text = blockText(sentences, b);
      if (scoredTexts.current[b] === text) continue;
      scoredTexts.current[b] = text;
      api
        .scoreText(text)
        .then((r) => {
          if (runId.current !== myRun || scoredTexts.current[b] !== text) return;
          setBlockScores((prev) => prev.map((v, i) => (i === b ? r.score : v)));
          setScoreWarning(false);
        })
        .catch(() => {
          if (runId.current === myRun) setScoreWarning(true);
        });
    }
  }, [sentences, api]);

  const load = (result: DetectionResult) => {
    const loaded: ViewSentence[] = result.sentences.map((s, i) => ({
      id: i,
      text: s.text,
      originalText: s.text,
      label: s.label,
      score: s.score,
      originalScore: s.score,
      para: s.para ?? 0,
      status: "idle",
    }));
    // Every sentence in a block carries that block's score, so the first one is the block score.
    const blocks = Math.ceil(loaded.length / BLOCK_SIZE);
    scoredTexts.current = Array.from({ length: blocks }, (_, b) => blockText(loaded, b));
    setBlockScores(Array.from({ length: blocks }, (_, b) => loaded[b * BLOCK_SIZE].score));
    setScoreWarning(false);
    replaceAll(loaded);
    setHeadings(result.headings ?? []);
    setInitialScore(result.summary.score);
  };

  const start = async (
    run: (signal: AbortSignal) => Promise<DetectionResult>,
    first: Exclude<Busy, null>,
    isUpload = false,
  ) => {
    controller.current?.abort();
    const ctl = new AbortController();
    controller.current = ctl;
    runId.current++;
    setError(null);
    setSoftError(false);
    setNotes([]);
    setTruncated(false);
    scoredTexts.current = [];
    queue.current = [];
    running.current = new Set();
    setBlockScores([]);
    replaceAll([]);
    setHeadings([]);
    setView("highlight");
    setBusy(first);
    try {
      const result = await run(ctl.signal);
      if (!result.sentences?.length) throw new ApiError("No sentences were found in the text.");
      load(result);
      setNotes(result.notes ?? []);
      // The backend cuts uploaded documents to MAX_ANALYSED_WORDS; the summary then reports exactly that many.
      setTruncated(isUpload && result.summary.total_words >= MAX_ANALYSED_WORDS);
    } catch (e) {
      if (!isAbort(e)) {
        setError(message(e));
        setSoftError(e instanceof ApiError && Boolean(e.code));
      }
    } finally {
      if (controller.current === ctl) setBusy(null);
    }
  };

  const onDetectText = (text: string) => start((signal) => api.detectText(text, signal), "detecting");

  const onUploadFile = (file: File) =>
    start(async (signal) => {
      const job = await api.uploadFile(file, signal);
      setBusy("processing");
      try {
        return await api.waitForJob(job.job_id, signal);
      } finally {
        // We hold the full result client-side; free the upload on the server.
        api.deleteJob(job.job_id);
      }
    }, "uploading", true);

  const onCancel = () => controller.current?.abort();

  const patch = (id: number, changes: Partial<ViewSentence>) =>
    update((prev) => prev.map((s) => (s.id === id ? { ...s, ...changes } : s)));

  // A sentence is humanized with its neighbours as context. So that the context is the CURRENT text of the
  // neighbours, requests start in click order, at most MAX_CONCURRENT_HUMANIZE at a time, the context is read at
  // the moment a request starts (not when it was clicked), and a sentence waits while one of its neighbours is
  // still being rewritten.
  const neighbourRunning = (id: number) => {
    const list = sentencesRef.current;
    const i = list.findIndex((s) => s.id === id);
    return [i - 1, i + 1].some((j) => j >= 0 && j < list.length && running.current.has(list[j].id));
  };

  const run = async (id: number) => {
    const list = sentencesRef.current;
    const idx = list.findIndex((s) => s.id === id);
    if (idx < 0) return;
    const target = list[idx];
    const myRun = runId.current;
    running.current.add(id);
    patch(id, { status: "loading", error: undefined, failedReason: undefined, startedAt: Date.now() });
    try {
      const res = await api.humanizeSentence({
        text: target.text,
        style,
        context_before: list[idx - 1]?.text ?? "",
        context_after: list[idx + 1]?.text ?? "",
      });
      if (runId.current !== myRun) return;
      const changed = !res.failed && res.engine !== "original" && res.humanized.trim() !== target.text.trim();
      patch(id, {
        text: changed ? res.humanized : target.text,
        score: res.new_score,
        engine: res.engine,
        failedReason: res.failed ? res.reason || "no safe rewrite found" : undefined,
        status: !changed ? "unchanged" : res.new_score < HUMAN_THRESHOLD ? "humanized" : "attempted",
      });
    } catch (e) {
      if (runId.current !== myRun) return;
      patch(id, { status: "error", error: message(e) });
    } finally {
      running.current.delete(id);
      pump();
    }
  };

  const pump = () => {
    while (running.current.size < MAX_CONCURRENT_HUMANIZE) {
      const pos = queue.current.findIndex((id) => !neighbourRunning(id));
      if (pos < 0) return;
      const [id] = queue.current.splice(pos, 1);
      void run(id);
    }
  };

  const onHumanize = (id: number) => {
    const current = sentencesRef.current.find((s) => s.id === id);
    if (!current || current.status === "loading" || current.status === "queued") return;
    patch(id, { status: "queued", error: undefined, failedReason: undefined });
    queue.current.push(id);
    pump();
  };

  const onCancelQueued = (id: number) => {
    queue.current = queue.current.filter((x) => x !== id);
    patch(id, { status: "idle" });
  };

  const onUndo = (id: number) =>
    update((prev) =>
      prev.map((s) =>
        s.id === id
          ? { ...s, text: s.originalText, score: s.originalScore, status: "idle", engine: undefined, failedReason: undefined }
          : s,
      ),
    );

  // Block-wise, like the detection score: mean over sentences of their block's current score.
  const nowScore = sentences.length
    ? Math.round(
        (sentences.reduce((sum, s, i) => sum + (blockScores[Math.floor(i / BLOCK_SIZE)] ?? s.originalScore), 0) /
          sentences.length) *
          100,
      )
    : 0;
  const humanizedCount = sentences.filter((s) => s.status === "humanized").length;
  const attemptedCount = sentences.filter((s) => s.status === "attempted").length;
  const aiRemaining = sentences.filter((s) => s.label === "ai" && s.status !== "humanized").length;
  // Compare needs at least one rewritten sentence (humanized or attempted); fall back to Highlight
  // if the last one is undone.
  const rewrittenCount = humanizedCount + attemptedCount;
  const activeView: View = rewrittenCount > 0 ? view : "highlight";

  return (
    <main className="mx-auto w-full max-w-4xl flex-1 px-4 py-10">
      <span className="rounded-full border border-blue-200 bg-blue-50 px-3 py-1 text-xs font-semibold text-blue-600">
        AI Humanizer Studio
      </span>
      <h1 className="mt-4 text-4xl font-bold tracking-tight text-slate-900">
        Detect AI sentences. <span className="text-brand">Humanize them.</span>
      </h1>
      <p className="mt-3 max-w-2xl text-slate-600">
        Paste text or upload a document. Sentences flagged as AI are highlighted — click one to rewrite it
        with the Humarin → T5 → Gemini → Rule-based pipeline.
      </p>

      <div className="mt-8 space-y-6">
        <InputCard
          style={style}
          onStyleChange={setStyle}
          busy={busy !== null}
          busyLabel={busy ? BUSY_LABEL[busy] : ""}
          onDetectText={onDetectText}
          onUploadFile={onUploadFile}
          onCancel={onCancel}
        />

        {!modelsReady && (
          <div className="rounded-xl border border-blue-200 bg-blue-50 px-4 py-3 text-sm text-blue-800">
            The AI models are still loading on the backend (about 30 seconds after it starts). Detection and
            humanizing will be slow until they are ready.
          </div>
        )}

        {error && (
          <div
            className={
              softError
                ? "rounded-xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-800"
                : "rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700"
            }
          >
            {error}
          </div>
        )}

        {sentences.length > 0 && (
          <>
            {notes.map((note) => (
              <div key={note} className="rounded-xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-800">
                {note}
              </div>
            ))}
            {truncated && (
              <div className="rounded-xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-800">
                Only the first {MAX_ANALYSED_WORDS.toLocaleString("en-US")} words of your document were analysed — the
                rest was not scored.
              </div>
            )}
            <ScoreSummary
              before={initialScore}
              now={nowScore}
              total={sentences.length}
              aiRemaining={aiRemaining}
              humanized={humanizedCount}
              attempted={attemptedCount}
              warning={scoreWarning}
            />
            <ViewToggle value={activeView} onChange={setView} compareDisabled={rewrittenCount === 0} />
            {activeView === "compare" ? (
              <CompareView sentences={sentences} before={initialScore} now={nowScore} />
            ) : (
              <SentenceView
                sentences={sentences}
                headings={headings}
                onHumanize={onHumanize}
                onUndo={onUndo}
                onCancelQueued={onCancelQueued}
              />
            )}
          </>
        )}
      </div>
    </main>
  );
}
