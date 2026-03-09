"use client";

export function ResultCard({
  title,
  children,
  delay,
  className = "",
  useArabicFont = false,
}: {
  title: string;
  children: React.ReactNode;
  delay: string;
  className?: string;
  useArabicFont?: boolean;
}) {
  return (
    <div
      className={`rounded-2xl border border-[var(--card-border)] bg-[var(--card-bg)] p-5 sm:p-6 shadow-[var(--card-shadow)] animate-fade-up ${className}`}
      style={{ animationDelay: delay }}
    >
      <h2 className={`${useArabicFont ? "font-arabic" : "font-display"} text-base font-semibold text-[var(--text)] mb-3`}>{title}</h2>
      <div className="max-h-64 overflow-y-auto">{children}</div>
    </div>
  );
}