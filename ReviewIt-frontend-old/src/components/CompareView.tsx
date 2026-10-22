"use client";

import { useState } from "react";
import EngineBadge from "./EngineBadge";
import type { ViewSentence } from "./SentenceView";

interface Props {
  sentences: ViewSentence[];
  before: number; // % AI at detection
  now: number; // % AI now
}

const MARK = "rounded px-1 py-0.5 box-decoration-clone";

function Original({ s }: { s: ViewSentence }) {
  return <span className={`${MARK} ${s.label === "ai" ? "bg-red-100" : ""}`}>{s.originalText}</span>;
}

function Humanized({ s }: { s: ViewSentence }) {
  if (s.status === "humanized" || s.status === "attempted") {
    return (
      <>
        <span className={`${MARK} ${s.status === "humanized" ? "bg-emerald-100" : "bg-amber-100"}`}>{s.text}</span>
        <EngineBadge engine={s.engine ?? "unknown"} />
      </>
    );
  }
  // Not humanized: still shows the original, in red if it is still flagged as AI.
  return (
    <>
      <span className={`${MARK} ${s.label === "ai" ? "bg-red-100" : ""}`}>{s.text}</span>
      {s.status === "unchanged" && <EngineBadge engine="original" />}
    </>
  );
}

export default function CompareView({ sentences, before, now }: Props) {
  const [onlyChanged, setOnlyChanged] = useState(false);
  const rows = onlyChanged
    ? sentences.filter((s) => s.status === "humanized" || s.status === "attempted")
    : sentences;

  return (
    <div className="rounded-2xl border border-slate-100 bg-white p-6 shadow-sm">
      <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
        <div className="flex flex-wrap items-center gap-3 text-xs text-slate-500">
          <Legend className="bg-red-100 ring-red-200" text="AI-detected" />
          <Legend className="bg-emerald-100 ring-emerald-200" text="Humanized" />
          <Legend className="bg-amber-100 ring-amber-200" text="Rewritten, still AI-like" />
        </div>
        <label className="flex cursor-pointer items-center gap-2 text-sm text-slate-600">
          <input
            type="checkbox"
            checked={onlyChanged}
            onChange={(e) => setOnlyChanged(e.target.checked)}
            className="h-4 w-4 accent-[#2563eb]"
          />
          Show only changed sentences
        </label>
      </div>

      <div className="hidden grid-cols-2 gap-6 border-b border-slate-100 pb-3 sm:grid">
        <ColumnTitle title="Original" score={before} />
        <ColumnTitle title="Humanized" score={now} />
      </div>

      {rows.length === 0 && <p className="py-6 text-sm text-slate-500">No sentences to show.</p>}

      {rows.map((s) => (
        <div key={s.id} className="grid grid-cols-1 gap-3 border-b border-slate-50 py-3 last:border-0 sm:grid-cols-2 sm:gap-6">
          <div className="leading-8 text-slate-800">
            <MobileLabel text="Original" />
            <Original s={s} />
          </div>
          <div className="leading-8 text-slate-800">
            <MobileLabel text="Humanized" />
            <Humanized s={s} />
          </div>
        </div>
      ))}
    </div>
  );
}

function ColumnTitle({ title, score }: { title: string; score: number }) {
  return (
    <div className="flex items-baseline justify-between">
      <span className="text-sm font-semibold text-slate-900">{title}</span>
      <span className="text-xs text-slate-500">
        AI score <span className="text-sm font-bold text-slate-900">{score}%</span>
      </span>
    </div>
  );
}

function MobileLabel({ text }: { text: string }) {
  return <div className="mb-1 text-[11px] font-semibold uppercase tracking-wide text-slate-400 sm:hidden">{text}</div>;
}

function Legend({ className, text }: { className: string; text: string }) {
  return (
    <span className="flex items-center gap-1.5">
      <span className={`h-3 w-3 rounded ring-1 ${className}`} />
      {text}
    </span>
  );
}
