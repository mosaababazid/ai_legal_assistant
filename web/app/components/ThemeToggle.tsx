"use client";

import { useState, useEffect } from "react";

export function ThemeToggle({ ariaLabel = "Theme wechseln" }: { ariaLabel?: string }) {
  const [dark, setDark] = useState(false);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    const stored = localStorage.getItem("theme") || "light";
    const isDark = stored === "dark";
    setDark(isDark);
    document.documentElement.classList.remove("dark");
    if (isDark) document.documentElement.classList.add("dark");
    if (!localStorage.getItem("theme")) localStorage.setItem("theme", "light");
    setMounted(true);
  }, []);

  const toggle = () => {
    const next = !dark;
    setDark(next);
    document.documentElement.classList.remove("dark");
    if (next) document.documentElement.classList.add("dark");
    localStorage.setItem("theme", next ? "dark" : "light");
  };

  if (!mounted) return <div className="w-10 h-10 rounded-full bg-[var(--border)] animate-pulse" aria-hidden />;

  return (
    <button
      type="button"
      onClick={toggle}
      className="w-10 h-10 flex items-center justify-center rounded-full border border-[var(--border)] bg-[var(--surface)] hover:bg-[var(--surface-hover)] transition-colors"
      aria-label={ariaLabel}
    >
      <span className="text-xl leading-none" aria-hidden>{dark ? "☀️" : "🌙"}</span>
    </button>
  );
}