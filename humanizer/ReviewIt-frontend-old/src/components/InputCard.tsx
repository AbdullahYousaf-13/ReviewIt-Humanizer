"use client";

import { useRef, useState } from "react";
import { ALLOWED_EXTENSIONS } from "@/lib/api";
import { STYLES } from "@/lib/config";
import StyleSelect from "./StyleSelect";

const SAMPLE =
  "Artificial intelligence has fundamentally transformed the landscape of modern education. It is important to note that these technologies offer numerous benefits for both students and educators. Furthermore, the integration of machine learning algorithms facilitates personalized learning experiences. Moreover, it is crucial to consider the ethical implications of such systems.";

interface Props {
  style: string;
  onStyleChange: (style: string) => void;
  busy: boolean;
  busyLabel: string;
  onDetectText: (text: string) => void;
  onUploadFile: (file: File) => void;
  onCancel: () => void;
}

export default function InputCard({
  style,
  onStyleChange,
  busy,
  busyLabel,
  onDetectText,
  onUploadFile,
  onCancel,
}: Props) {
  const [mode, setMode] = useState<"text" | "file">("text");
  const [text, setText] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [fileError, setFileError] = useState<string | null>(null);
  const [dragging, setDragging] = useState(false);
  const fileInput = useRef<HTMLInputElement>(null);

  const words = text.trim() ? text.trim().split(/\s+/).length : 0;
  const canSubmit = !busy && (mode === "text" ? text.trim().length > 0 : file !== null);

  const pickFile = (f: File | null) => {
    setFileError(null);
    if (!f) return setFile(null);
    const ext = f.name.slice(f.name.lastIndexOf(".")).toLowerCase();
    if (!ALLOWED_EXTENSIONS.includes(ext)) {
      setFile(null);
      setFileError(`Unsupported file type. Use ${ALLOWED_EXTENSIONS.join(", ")}.`);
      return;
    }
    setFile(f);
  };

  const onDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setDragging(false);
    if (!busy) pickFile(e.dataTransfer.files?.[0] ?? null);
  };

  const submit = () => {
    if (!canSubmit) return;
    if (mode === "text") onDetectText(text);
    else if (file) onUploadFile(file);
  };

  return (
    <div className="rounded-2xl border border-slate-100 bg-white p-6 shadow-sm">
      <div className="mb-4 flex gap-2">
        {(["text", "file"] as const).map((m) => (
          <button
            key={m}
            type="button"
            disabled={busy}
            onClick={() => setMode(m)}
            className={`rounded-full px-4 py-1.5 text-sm font-semibold transition ${
              mode === m ? "bg-brand text-white" : "bg-slate-100 text-slate-600 hover:bg-slate-200"
            }`}
          >
            {m === "text" ? "Paste text" : "Upload file"}
          </button>
        ))}
      </div>

      {mode === "text" ? (
        <>
          <textarea
            value={text}
            onChange={(e) => setText(e.target.value)}
            disabled={busy}
            rows={9}
            placeholder="Paste your text here…"
            className="w-full resize-y rounded-xl border border-slate-200 p-4 text-sm leading-6 outline-none focus:border-brand focus:ring-2 focus:ring-blue-100"
          />
          <div className="mt-2 flex items-center justify-between text-xs text-slate-500">
            <span>
              {words} words · {text.length} characters
            </span>
            <button
              type="button"
              disabled={busy}
              onClick={() => setText(SAMPLE)}
              className="font-medium text-brand hover:text-brand-hover"
            >
              Try a sample
            </button>
          </div>
        </>
      ) : (
        <div
          onClick={() => !busy && fileInput.current?.click()}
          onDragOver={(e) => {
            e.preventDefault();
            if (!busy) setDragging(true);
          }}
          onDragLeave={() => setDragging(false)}
          onDrop={onDrop}
          className={`flex cursor-pointer flex-col items-center justify-center rounded-xl border-2 border-dashed px-4 py-12 text-center transition hover:border-brand ${
            dragging ? "border-brand bg-blue-50" : "border-slate-200"
          }`}
        >
          <input
            ref={fileInput}
            type="file"
            accept={ALLOWED_EXTENSIONS.join(",")}
            className="hidden"
            onChange={(e) => pickFile(e.target.files?.[0] ?? null)}
          />
          <p className="text-sm font-semibold text-slate-700">{file ? file.name : "Click to choose a file, or drag it here"}</p>
          <p className="mt-1 text-xs text-slate-500">{ALLOWED_EXTENSIONS.join("  ")}</p>
          {fileError && <p className="mt-2 text-xs font-medium text-red-600">{fileError}</p>}
        </div>
      )}

      <div className="mt-5 flex flex-wrap items-center gap-3">
        <div className="flex items-center gap-3 text-sm font-medium text-slate-500">
          <span id="style-label">Style</span>
          <StyleSelect
            value={style}
            options={STYLES}
            onChange={onStyleChange}
            disabled={busy}
            labelledBy="style-label"
          />
        </div>
        <button
          type="button"
          onClick={submit}
          disabled={!canSubmit}
          className="ml-auto rounded-xl bg-brand px-6 py-2.5 text-sm font-semibold text-white transition hover:bg-brand-hover disabled:cursor-not-allowed disabled:opacity-50"
        >
          {busy ? busyLabel : "Detect AI"}
        </button>
        {busy && (
          <button type="button" onClick={onCancel} className="text-sm font-medium text-slate-500 hover:text-slate-800">
            Cancel
          </button>
        )}
      </div>
    </div>
  );
}
