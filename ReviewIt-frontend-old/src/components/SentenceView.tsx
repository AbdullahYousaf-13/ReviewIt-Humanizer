"use client";

import { Fragment, useEffect, useMemo, useState } from "react";
import type { DetectedHeading } from "@/lib/types";
import EngineBadge from "./EngineBadge";

export interface ViewSentence {
  id: number;
  text: string;
  originalText: string;
  label: "ai" | "human";
  score: number;
  originalScore: number;
  /** Paragraph number from the detector (sentences of one paragraph share it). */
  para: number;
  // queued = waiting for a free slot; humanized = rewrite scores below the human threshold;
  // attempted = rewritten but still AI-like; unchanged = no safe, clearly better rewrite (original kept)
  status: "idle" | "queued" | "loading" | "humanized" | "attempted" | "unchanged" | "error";
  startedAt?: number; // ms timestamp when humanizing started
  engine?: string;
  error?: string;
  /** Why the original was kept (status "unchanged" after a failed humanization). */
  failedReason?: string;
}

interface Props {
  sentences: ViewSentence[];
  headings?: DetectedHeading[];
  onHumanize: (id: number) => void;
  onUndo: (id: number) => void;
  onCancelQueued: (id: number) => void;
}

export default function SentenceView({ sentences, headings = [], onHumanize, onUndo, onCancelQueued }: Props) {
  // Consecutive sentences with the same paragraph number form one paragraph.
  const paragraphs = useMemo(() => {
    const groups: { para: number; items: ViewSentence[] }[] = [];
    for (const s of sentences) {
      const last = groups[groups.length - 1];
      if (last && last.para === s.para) last.items.push(s);
      else groups.push({ para: s.para, items: [s] });
    }
    return groups;
  }, [sentences]);

  const lastPara = paragraphs.length ? paragraphs[paragraphs.length - 1].para : -1;
  const headingsBefore = (para: number) => headings.filter((h) => h.para === para);
  const trailingHeadings = headings.filter((h) => h.para > lastPara);

  return (
    <div className="rounded-2xl border border-slate-100 bg-white p-6 shadow-sm">
      <div className="mb-4 flex flex-wrap items-center gap-3 text-xs text-slate-500">
        <Legend className="bg-red-100 ring-red-200" text="AI-detected (click to humanize)" />
        <Legend className="bg-emerald-100 ring-emerald-200" text="Humanized" />
        <Legend className="bg-amber-100 ring-amber-200" text="Rewritten, still AI-like" />
        <Legend className="bg-white ring-slate-200" text="Human" />
      </div>
      <div className="space-y-4">
        {paragraphs.map((group) => (
          <Fragment key={`${group.para}-${group.items[0].id}`}>
            {headingsBefore(group.para).map((h, i) => (
              <Heading key={`h-${group.para}-${i}`} text={h.text} />
            ))}
            <p className="leading-8 text-slate-800">
              {group.items.map((s) => (
                <Sentence key={s.id} s={s} onHumanize={onHumanize} onUndo={onUndo} onCancelQueued={onCancelQueued} />
              ))}
            </p>
          </Fragment>
        ))}
        {trailingHeadings.map((h, i) => (
          <Heading key={`h-end-${i}`} text={h.text} />
        ))}
      </div>
    </div>
  );
}

function Heading({ text }: { text: string }) {
  return <h3 className="pt-2 text-sm font-semibold text-slate-500">{text}</h3>;
}

function Elapsed({ since }: { since: number }) {
  const [now, setNow] = useState(since);
  useEffect(() => {
    const id = setInterval(() => setNow(Date.now()), 1000);
    return () => clearInterval(id);
  }, []);
  const secs = Math.max(0, Math.floor((now - since) / 1000));
  return (
    <span className="ml-1 text-xs font-medium text-brand">
      humanizing… {secs}s
      {secs >= 25 && " — taking longer than usual, the models are busy"}
    </span>
  );
}

function Legend({ className, text }: { className: string; text: string }) {
  return (
    <span className="flex items-center gap-1.5">
      <span className={`h-3 w-3 rounded ring-1 ${className}`} />
      {text}
    </span>
  );
}

function Sentence({
  s,
  onHumanize,
  onUndo,
  onCancelQueued,
}: {
  s: ViewSentence;
  onHumanize: (id: number) => void;
  onUndo: (id: number) => void;
  onCancelQueued: (id: number) => void;
}) {
  const base = "rounded px-1 py-0.5 box-decoration-clone";

  if (s.status === "humanized" || s.status === "attempted" || s.status === "unchanged") {
    const color =
      s.status === "humanized" ? "bg-emerald-100" : s.status === "attempted" ? "bg-amber-100" : "bg-slate-100";
    return (
      <>
        <span className={`${base} ${color}`}>{s.text}</span>
        <EngineBadge engine={s.engine ?? "unknown"} score={s.score} />
        {s.status === "unchanged" && s.failedReason && (
          <span className="ml-1 text-xs font-medium text-amber-700" title={s.failedReason}>
            kept the original — no safe, clearly better rewrite found
          </span>
        )}
        <button
          type="button"
          onClick={() => onUndo(s.id)}
          className="ml-1 text-xs font-medium text-slate-400 hover:text-slate-700"
          title="Restore the original sentence"
        >
          ↺ undo
        </button>{" "}
      </>
    );
  }

  if (s.status === "queued") {
    return (
      <>
        <span className={`${base} bg-blue-50 text-slate-500`}>{s.text}</span>
        <span className="ml-1 text-xs font-medium text-slate-500">waiting for a free slot…</span>
        <button
          type="button"
          onClick={() => onCancelQueued(s.id)}
          className="ml-1 text-xs font-medium text-slate-400 hover:text-slate-700"
        >
          cancel
        </button>{" "}
      </>
    );
  }

  if (s.status === "loading") {
    return (
      <>
        <span className={`${base} animate-pulse bg-blue-50 text-slate-500`}>{s.text}</span>
        <Elapsed since={s.startedAt ?? 0} />{" "}
      </>
    );
  }

  if (s.label === "ai") {
    return (
      <>
        <button
          type="button"
          onClick={() => onHumanize(s.id)}
          className={`${base} cursor-pointer bg-red-100 text-left transition hover:bg-red-200`}
          title={`AI score ${s.score.toFixed(2)} — click to humanize`}
        >
          {s.text}
        </button>
        {s.status === "error" && (
          <span className="ml-1 text-xs font-medium text-red-600">{s.error ?? "Failed"} — click to retry</span>
        )}{" "}
      </>
    );
  }

  return <span className={base}>{s.text} </span>;
}
