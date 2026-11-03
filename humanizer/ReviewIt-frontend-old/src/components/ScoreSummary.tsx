interface Props {
  before: number; // block-wise % AI at detection
  now: number; // block-wise % AI after replacements
  total: number;
  aiRemaining: number;
  humanized: number; // rewrites that now score below the human threshold
  attempted: number; // rewritten but still AI-like
  warning?: boolean; // a block could not be re-scored
}

function Meter({ label, value }: { label: string; value: number }) {
  const color = value >= 40 ? "bg-red-500" : "bg-emerald-500";
  return (
    <div className="flex-1">
      <div className="mb-1 flex items-baseline justify-between text-xs font-medium text-slate-500">
        <span>{label}</span>
        <span className="text-base font-bold text-slate-900">{value}%</span>
      </div>
      <div className="h-2 overflow-hidden rounded-full bg-slate-100">
        <div className={`h-full rounded-full transition-all ${color}`} style={{ width: `${value}%` }} />
      </div>
    </div>
  );
}

export default function ScoreSummary({ before, now, total, aiRemaining, humanized, attempted, warning }: Props) {
  return (
    <div className="rounded-2xl border border-slate-100 bg-white p-5 shadow-sm">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center">
        <Meter label="AI score at detection" value={before} />
        <span className="hidden text-slate-300 sm:block">➔</span>
        <Meter label="AI score now" value={now} />
      </div>
      <p className="mt-3 text-xs text-slate-500">
        {total} sentences · {aiRemaining} still flagged as AI · {humanized} humanized
        {attempted > 0 && ` · ${attempted} attempted (rewritten, still AI-like)`}. Scores are block-wise: the
        detector scores each block of 4 sentences together. The score on each badge is for that sentence alone.
      </p>
      {warning && (
        <p className="mt-1 text-xs font-medium text-amber-600">
          Couldn&apos;t re-score a block — &quot;AI score now&quot; may be out of date.
        </p>
      )}
    </div>
  );
}
