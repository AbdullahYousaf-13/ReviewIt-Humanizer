export type Label = "ai" | "human";

/** Sentence as returned by the detector. */
export interface DetectedSentence {
  text: string;
  label: Label;
  score: number;
  /** Paragraph number in the document (sentences of one paragraph share it). */
  para?: number;
}

/** A heading found in the document; shown just before the paragraph with number `para`. */
export interface DetectedHeading {
  text: string;
  para: number;
}

export interface DetectionSummary {
  total_sentences: number;
  ai_sentences: number;
  human_sentences: number;
  average_score: number;
  score: number; // average AI score as a percentage (0-100)
  total_words: number;
  total_characters: number;
}

export interface DetectionResult {
  sentences: DetectedSentence[];
  headings?: DetectedHeading[];
  /** Things the person should know about the file (e.g. "2 of 30 pages are scanned images and were skipped"). */
  notes?: string[];
  summary: DetectionSummary;
  filename?: string;
}

export type JobStatus = "processing" | "done" | "error";

export interface JobStarted {
  job_id: string;
  status: JobStatus;
  filename: string;
}

export interface JobStatusResponse {
  job_id: string;
  status: JobStatus;
  filename: string;
  elapsed_seconds: number;
  error: string | null;
  /** Set for files the app does not support ("scanned", "protected"): shown as a notice, not as a failure. */
  error_code?: string | null;
}

export type Engine = "humarin" | "t5" | "gemini" | "rule_based" | "original";

export interface HumanizeSentenceRequest {
  text: string;
  style: string;
  context_before?: string;
  context_after?: string;
}

export interface HumanizeSentenceResult {
  original: string;
  humanized: string;
  original_score: number;
  new_score: number;
  improvement: number;
  engine: Engine | string;
  processing_time: number;
  /** True when no safe, clearly better rewrite was found: `humanized` is then the original sentence. */
  failed: boolean;
  reason: string;
}

export interface HealthStatus {
  status: string;
  /** False while the backend is still loading its models at start-up. */
  models_ready?: boolean;
}
