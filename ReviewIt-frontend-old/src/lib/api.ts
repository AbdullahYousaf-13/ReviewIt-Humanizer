import type {
  DetectionResult,
  HealthStatus,
  HumanizeSentenceRequest,
  HumanizeSentenceResult,
  JobStarted,
  JobStatusResponse,
} from "./types";

export const DEFAULT_API_URL = "http://127.0.0.1:5000";
export const ALLOWED_EXTENSIONS = [".pdf", ".docx", ".doc", ".txt"];

export class ApiError extends Error {
  /** Set when the file itself cannot be used ("scanned", "protected"): a notice for the person, not a failure. */
  code?: string;

  constructor(message: string, code?: string) {
    super(message);
    this.code = code;
  }
}

const POLL_INTERVAL_MS = 1500;

const json = (body: unknown, signal?: AbortSignal): RequestInit => ({
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify(body),
  signal,
});

const sleep = (ms: number, signal?: AbortSignal) =>
  new Promise<void>((resolve, reject) => {
    const id = setTimeout(resolve, ms);
    signal?.addEventListener(
      "abort",
      () => {
        clearTimeout(id);
        reject(new DOMException("Aborted", "AbortError"));
      },
      { once: true },
    );
  });

/** Typed client for the Flask backend. `baseUrl` is supplied at runtime (see page.tsx). */
export function createApi(baseUrl: string) {
  const API_URL = baseUrl.replace(/\/$/, "");

  async function request<T>(path: string, init?: RequestInit): Promise<T> {
    let res: Response;
    try {
      res = await fetch(`${API_URL}${path}`, { cache: "no-store", ...init });
    } catch (err) {
      if (err instanceof DOMException && err.name === "AbortError") throw err;
      throw new ApiError(`Cannot reach the backend at ${API_URL}. Is it running?`);
    }
    const body = await res.json().catch(() => null);
    if (!res.ok) {
      throw new ApiError(body?.error ?? `Request failed (${res.status})`);
    }
    return body as T;
  }

  const getHealth = (signal?: AbortSignal) => request<HealthStatus>("/api/health", { signal });

  /** Paste-text path: synchronous detection. */
  const detectText = (text: string, signal?: AbortSignal) =>
    request<DetectionResult>("/api/detect-text", json({ text }, signal));

  /** Upload path, step 1: start an async detection job. */
  const uploadFile = (file: File, signal?: AbortSignal) => {
    const form = new FormData();
    form.append("file", file);
    return request<JobStarted>("/api/detect", { method: "POST", body: form, signal });
  };

  const getJobStatus = (jobId: string, signal?: AbortSignal) =>
    request<JobStatusResponse>(`/api/status/${jobId}`, { signal });

  const getJobResult = (jobId: string, signal?: AbortSignal) =>
    request<DetectionResult>(`/api/result/${jobId}`, { signal });

  const deleteJob = async (jobId: string): Promise<void> => {
    try {
      await fetch(`${API_URL}/api/status/${jobId}`, { method: "DELETE" });
    } catch {
      // best-effort cleanup
    }
  };

  /** Upload path, steps 2-3: poll until the job finishes, then fetch the result. */
  const waitForJob = async (jobId: string, signal?: AbortSignal): Promise<DetectionResult> => {
    for (;;) {
      const status = await getJobStatus(jobId, signal);
      if (status.status === "error") {
        throw new ApiError(status.error ?? "The document could not be processed.", status.error_code ?? undefined);
      }
      if (status.status === "done") return getJobResult(jobId, signal);
      await sleep(POLL_INTERVAL_MS, signal);
    }
  };

  /** Score a text exactly as the detector scores a block (one BERT pass over the whole string). */
  const scoreText = (text: string, signal?: AbortSignal) =>
    request<{ score: number }>("/api/detector-score", json({ text }, signal));

  const humanizeSentence = async (
    req: HumanizeSentenceRequest,
    signal?: AbortSignal,
  ): Promise<HumanizeSentenceResult> => {
    // Backend nests the fields under `data` (and mirrors some at top level).
    const res = await request<{ data?: Partial<HumanizeSentenceResult>; processing_time?: number }>(
      "/api/humanize-sentence",
      json(req, signal),
    );
    const d = res.data;
    if (!d || typeof d.humanized !== "string") {
      throw new ApiError("Unexpected response from the humanizer.");
    }
    return {
      original: d.original ?? req.text,
      humanized: d.humanized,
      original_score: d.original_score ?? 0,
      new_score: d.new_score ?? 0,
      improvement: d.improvement ?? 0,
      engine: d.engine ?? "unknown",
      processing_time: res.processing_time ?? 0,
      failed: d.failed ?? false,
      reason: d.reason ?? "",
    };
  };

  return {
    getHealth,
    detectText,
    uploadFile,
    getJobStatus,
    getJobResult,
    deleteJob,
    waitForJob,
    scoreText,
    humanizeSentence,
  };
}

export type Api = ReturnType<typeof createApi>;
