export type View = "highlight" | "compare";

const OPTIONS: { value: View; label: string }[] = [
  { value: "highlight", label: "Highlight" },
  { value: "compare", label: "Compare" },
];

interface Props {
  value: View;
  onChange: (view: View) => void;
  compareDisabled: boolean;
}

export default function ViewToggle({ value, onChange, compareDisabled }: Props) {
  return (
    <div className="flex items-center gap-3">
      <span className="text-sm font-medium text-slate-500">View</span>
      <div
        role="radiogroup"
        aria-label="View"
        className="inline-flex rounded-full border border-slate-200 bg-white p-1 shadow-sm"
      >
        {OPTIONS.map(({ value: v, label }) => {
          const disabled = v === "compare" && compareDisabled;
          const active = value === v;
          return (
            <button
              key={v}
              type="button"
              role="radio"
              aria-checked={active}
              disabled={disabled}
              onClick={() => onChange(v)}
              title={disabled ? "Rewrite at least one sentence to compare" : undefined}
              className={`rounded-full px-4 py-1.5 text-sm font-semibold transition ${
                active
                  ? "bg-brand text-white"
                  : "text-slate-600 hover:bg-slate-100 disabled:cursor-not-allowed disabled:opacity-40 disabled:hover:bg-transparent"
              }`}
            >
              {label}
            </button>
          );
        })}
      </div>
    </div>
  );
}
