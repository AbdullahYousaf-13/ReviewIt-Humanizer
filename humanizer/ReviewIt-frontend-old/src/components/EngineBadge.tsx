const ENGINES: Record<string, { label: string; className: string }> = {
  humarin: { label: "Tier 1 · Humarin", className: "bg-emerald-50 text-emerald-700 border-emerald-200" },
  t5: { label: "Tier 2 · T5", className: "bg-violet-50 text-violet-700 border-violet-200" },
  gemini: { label: "Tier 3 · Gemini", className: "bg-blue-50 text-blue-700 border-blue-200" },
  rule_based: { label: "Tier 4 · Rule-based", className: "bg-orange-50 text-orange-700 border-orange-200" },
  original: { label: "No better rewrite", className: "bg-slate-50 text-slate-600 border-slate-200" },
};

export default function EngineBadge({ engine, score }: { engine: string; score?: number }) {
  const { label, className } = ENGINES[engine] ?? {
    label: engine,
    className: "bg-slate-50 text-slate-600 border-slate-200",
  };
  return (
    <span
      className={`ml-1 inline-flex items-center gap-1 rounded-full border px-2 py-0.5 align-middle text-[11px] font-semibold ${className}`}
    >
      {label}
      {score !== undefined && <span className="font-mono opacity-80">· {score.toFixed(2)}</span>}
    </span>
  );
}
