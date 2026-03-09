"use client";

import { useRef, useEffect, useState } from "react";

export type CustomSelectOption = { value: string; label: string };

type Props = {
  value: string;
  options: CustomSelectOption[];
  onChange: (value: string) => void;
  isRtl?: boolean;
  useArabicFont?: boolean;
  id?: string;
  "aria-label"?: string;
  className?: string;
};

export function CustomSelect({
  value,
  options,
  onChange,
  isRtl = false,
  id,
  "aria-label": ariaLabel,
  className = "",
}: Props) {
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false);
    };
    if (open) {
      document.addEventListener("mousedown", handleClickOutside);
      return () => document.removeEventListener("mousedown", handleClickOutside);
    }
  }, [open]);

  const selected = options.find((o) => o.value === value) ?? options[0];
  const fontClass = isRtl ? "font-arabic" : "";

  return (
    <div ref={ref} className={`relative ${className}`}>
      <button
        type="button"
        id={id}
        aria-label={ariaLabel}
        aria-haspopup="listbox"
        aria-expanded={open}
        aria-selected={undefined}
        onClick={() => setOpen((o) => !o)}
        className={`
          w-full rounded-xl border border-[var(--card-border)] bg-[var(--card-bg)]
          text-[var(--text)] px-4 py-3 text-sm shadow-[var(--card-shadow)]
          focus:ring-2 focus:ring-[var(--accent)]/30 focus:border-[var(--accent)] outline-none transition
          flex items-center justify-between gap-2
          ${isRtl ? "flex-row-reverse text-right" : "text-left"}
          ${open ? "ring-2 ring-[var(--accent)]/30 border-[var(--accent)]" : ""}
          ${fontClass}
        `}
      >
        <span>{selected.label}</span>
        <span
          className={`flex shrink-0 text-[var(--text-muted)] transition-transform duration-200 ${open ? "rotate-180" : ""}`}
          aria-hidden
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        </span>
      </button>

      {open && (
        <ul
          role="listbox"
          aria-activedescendant={value}
          className={`
            absolute z-50 mt-2 left-0 right-0 rounded-xl
            border border-[var(--card-border)] bg-[var(--card-bg)]
            py-1 max-h-60 overflow-auto
            animate-fade-in
            ${fontClass}
          `}
          style={{
            boxShadow: "0 12px 40px -8px rgba(0,0,0,0.15), 0 0 0 1px var(--card-border)",
          }}
        >
          {options.map((opt) => (
            <li
              key={opt.value}
              role="option"
              aria-selected={opt.value === value}
              onClick={() => {
                onChange(opt.value);
                setOpen(false);
              }}
              className={`
                px-4 py-3 cursor-pointer text-sm transition-colors
                ${isRtl ? "text-right" : "text-left"}
                ${opt.value === value ? "bg-[var(--accent)]/15 text-[var(--accent)] font-medium" : "text-[var(--text)] hover:bg-[var(--dropzone-hover)]"}
              `}
            >
              {opt.label}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}