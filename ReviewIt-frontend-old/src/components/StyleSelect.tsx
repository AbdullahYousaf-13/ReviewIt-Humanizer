"use client";

import { useEffect, useRef, useState } from "react";

interface Props {
  value: string;
  options: readonly string[];
  onChange: (value: string) => void;
  disabled?: boolean;
  labelledBy?: string;
}

/** Pill button that opens a styled menu (the browser's own <select> list cannot be styled). */
export default function StyleSelect({ value, options, onChange, disabled, labelledBy }: Props) {
  const [open, setOpen] = useState(false);
  const [active, setActive] = useState(0);
  const root = useRef<HTMLDivElement>(null);
  const button = useRef<HTMLButtonElement>(null);
  const list = useRef<HTMLUListElement>(null);

  // Close when you click anywhere outside.
  useEffect(() => {
    if (!open) return;
    const onPointerDown = (e: PointerEvent) => {
      if (!root.current?.contains(e.target as Node)) setOpen(false);
    };
    document.addEventListener("pointerdown", onPointerDown);
    return () => document.removeEventListener("pointerdown", onPointerDown);
  }, [open]);

  // Move keyboard focus into the menu when it opens.
  useEffect(() => {
    if (open) list.current?.focus();
  }, [open]);

  const openMenu = () => {
    setActive(Math.max(0, options.indexOf(value)));
    setOpen(true);
  };

  const choose = (v: string) => {
    onChange(v);
    setOpen(false);
    button.current?.focus();
  };

  const onButtonKey = (e: React.KeyboardEvent) => {
    if (e.key === "ArrowDown" || e.key === "ArrowUp") {
      e.preventDefault();
      openMenu();
    }
  };

  const onListKey = (e: React.KeyboardEvent) => {
    const last = options.length - 1;
    switch (e.key) {
      case "ArrowDown":
        e.preventDefault();
        setActive((i) => (i >= last ? 0 : i + 1));
        break;
      case "ArrowUp":
        e.preventDefault();
        setActive((i) => (i <= 0 ? last : i - 1));
        break;
      case "Home":
        e.preventDefault();
        setActive(0);
        break;
      case "End":
        e.preventDefault();
        setActive(last);
        break;
      case "Enter":
      case " ":
        e.preventDefault();
        choose(options[active]);
        break;
      case "Escape":
        e.preventDefault();
        setOpen(false);
        button.current?.focus();
        break;
      case "Tab":
        setOpen(false);
        break;
    }
  };

  return (
    <div ref={root} className="relative inline-block">
      <button
        ref={button}
        type="button"
        disabled={disabled}
        aria-haspopup="listbox"
        aria-expanded={open}
        aria-labelledby={labelledBy}
        onClick={() => (open ? setOpen(false) : openMenu())}
        onKeyDown={onButtonKey}
        className={`inline-flex cursor-pointer items-center gap-3 rounded-full border bg-white py-2 pl-4 pr-3.5 text-sm font-semibold capitalize text-slate-700 shadow-sm outline-none transition hover:bg-slate-50 focus-visible:border-brand focus-visible:ring-2 focus-visible:ring-blue-100 disabled:cursor-not-allowed disabled:opacity-50 ${
          open ? "border-brand ring-2 ring-blue-100" : "border-slate-200"
        }`}
      >
        {value}
        <svg
          aria-hidden="true"
          viewBox="0 0 20 20"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
          className={`h-4 w-4 text-slate-400 transition-transform ${open ? "rotate-180" : ""}`}
        >
          <path d="M5 7.5l5 5 5-5" />
        </svg>
      </button>

      {open && (
        <ul
          ref={list}
          role="listbox"
          tabIndex={-1}
          aria-labelledby={labelledBy}
          aria-activedescendant={`style-option-${active}`}
          onKeyDown={onListKey}
          className="absolute bottom-full left-0 z-20 mb-2 w-48 overflow-hidden rounded-2xl border border-slate-100 bg-white p-1.5 shadow-lg outline-none"
        >
          {options.map((opt, i) => {
            const selected = opt === value;
            return (
              <li
                key={opt}
                id={`style-option-${i}`}
                role="option"
                aria-selected={selected}
                onClick={() => choose(opt)}
                onMouseEnter={() => setActive(i)}
                className={`flex cursor-pointer items-center justify-between rounded-xl px-3 py-2 text-sm capitalize transition ${
                  selected ? "font-semibold text-brand" : "font-medium text-slate-700"
                } ${i === active ? "bg-blue-50" : ""}`}
              >
                {opt}
                {selected && (
                  <svg
                    aria-hidden="true"
                    viewBox="0 0 20 20"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="2.2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    className="h-4 w-4"
                  >
                    <path d="M4.5 10.5l3.5 3.5 7.5-8" />
                  </svg>
                )}
              </li>
            );
          })}
        </ul>
      )}
    </div>
  );
}
