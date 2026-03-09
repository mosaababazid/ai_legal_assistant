"use client";

import { useCallback, useEffect, useState } from "react";
import { ResultCard } from "./components/ResultCard";
import { ThemeToggle } from "./components/ThemeToggle";
import { Footer } from "./components/Footer";
import { CustomSelect } from "./components/CustomSelect";
import { translations, type UiLocale } from "./lib/translations";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000";
const UI_LOCALE_KEY = "ui-locale";

function setStoredUiLocale(locale: UiLocale) {
  if (typeof localStorage === "undefined") return;
  localStorage.setItem(UI_LOCALE_KEY, locale);
  document.documentElement.setAttribute("data-ui-locale", locale);
}

type Result = {
  original_text: string;
  summary?: string;
  legal_recommendation?: string;
  used_paragraphs?: string[];
  disclaimer?: string;
};

export default function Home() {
  const [uiLocale, setUiLocale] = useState<UiLocale>("de");

  useEffect(() => {
    const stored = localStorage.getItem(UI_LOCALE_KEY);
    if (stored === "ar" || stored === "de") setUiLocale(stored);
  }, []);
  const [file, setFile] = useState<File | null>(null);
  const [language, setLanguage] = useState<"de" | "ar">("de");
  const [mode, setMode] = useState<"summary" | "legal_advice">("summary");
  const [loading, setLoading] = useState(false);
  const [uploadPercent, setUploadPercent] = useState(0);
  const [result, setResult] = useState<Result | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [drag, setDrag] = useState(false);

  const t = translations[uiLocale];
  const isRtl = uiLocale === "ar";

  const onDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setDrag(false);
    const f = e.dataTransfer?.files?.[0];
    if (f && (f.type === "application/pdf" || f.type.startsWith("image/"))) setFile(f);
  }, []);

  const onDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setDrag(true);
  }, []);

  const onDragLeave = useCallback(() => setDrag(false), []);

  const onSubmit = useCallback(
    async (e: React.FormEvent) => {
      e.preventDefault();
      if (!file) return;
      setError(null);
      setResult(null);
      setLoading(true);
      setUploadPercent(0);

      const formData = new FormData();
      formData.append("file", file);
      formData.append("language", language);
      formData.append("mode", mode);

      const xhr = new XMLHttpRequest();
      xhr.open("POST", `${API_URL}/api/extract-summarize`);

      xhr.upload.addEventListener("progress", (ev) => {
        if (ev.lengthComputable) setUploadPercent(Math.round((ev.loaded / ev.total) * 100));
      });

      const done = (err?: string) => {
        setLoading(false);
        setUploadPercent(0);
        if (err) setError(err);
      };

      xhr.onload = () => {
        if (xhr.status >= 200 && xhr.status < 300) {
          try {
            setResult(JSON.parse(xhr.responseText) as Result);
            done();
          } catch {
            done(t.errParse);
          }
        } else {
          try {
            const body = JSON.parse(xhr.responseText);
            done(body.detail ?? `${t.errServer} ${xhr.status}`);
          } catch {
            done(`${t.errServer} (HTTP ${xhr.status}).`);
          }
        }
      };

      xhr.onerror = () => done(t.errRequest);
      xhr.send(formData);
    },
    [file, language, mode, t]
  );

  return (
    <div
      className={`min-h-screen bg-grid-arabic text-[var(--text)] relative ${isRtl ? "font-arabic" : ""}`}
      dir={isRtl ? "rtl" : "ltr"}
      lang={isRtl ? "ar" : "de"}
    >
      <header className="relative z-10 flex justify-between items-center px-5 sm:px-8 lg:px-12 py-5 sm:py-6">
        <a
          href="/"
          className={`${isRtl ? "font-arabic" : "font-display tracking-tight"} text-lg sm:text-xl font-semibold text-[var(--text)] hover:opacity-80 transition-opacity`}
        >
          {t.siteName}
        </a>
        <div className="flex items-center gap-2 sm:gap-3">
          <div className="flex rounded-full p-1 bg-[var(--card-bg)] border border-[var(--card-border)] shadow-[var(--card-shadow)]">
            <button
              type="button"
              onClick={() => {
                setUiLocale("de");
                setStoredUiLocale("de");
              }}
              className={`rounded-full px-3 py-1.5 text-sm font-medium transition-colors ${
                uiLocale === "de"
                  ? "bg-[var(--accent)] text-white dark:text-[var(--bg)]"
                  : "text-[var(--text-muted)] hover:text-[var(--text)]"
              }`}
            >
              {t.langDe}
            </button>
            <button
              type="button"
              onClick={() => {
                setUiLocale("ar");
                setStoredUiLocale("ar");
              }}
              className={`rounded-full px-3 py-1.5 text-sm font-medium transition-colors ${
                uiLocale === "ar"
                  ? "bg-[var(--accent)] text-white dark:text-[var(--bg)]"
                  : "text-[var(--text-muted)] hover:text-[var(--text)]"
              }`}
            >
              {t.langAr}
            </button>
          </div>
          <ThemeToggle ariaLabel={t.themeLabel} />
        </div>
      </header>

      <main className="relative z-10 max-w-5xl mx-auto px-5 sm:px-8 lg:px-12 pb-20 sm:pb-28">
        <div className="grid lg:grid-cols-[1fr,1.15fr] gap-12 lg:gap-20 items-start pt-6 sm:pt-10 lg:pt-16">
          <div className="animate-fade-up" style={{ animationDelay: "0ms" }}>
            <p className={`text-xs font-medium uppercase text-[var(--accent)] mb-4 ${isRtl ? "font-arabic" : "tracking-[0.18em]"}`}>
              {t.tagline}
            </p>
            <h1 className={`${isRtl ? "font-arabic leading-[2.15]" : "font-display leading-[1.12]"} text-3xl sm:text-4xl lg:text-5xl font-bold max-w-lg text-[var(--text)]`}>
              {t.heroTitle}
            </h1>
            <p className="mt-5 text-[var(--text-muted)] text-base sm:text-lg max-w-md leading-relaxed">
              {t.heroDesc}
            </p>
          </div>

          <div className="animate-fade-up lg:pt-2" style={{ animationDelay: "80ms" }}>
            <form onSubmit={onSubmit} className="space-y-5">
              <div
                onDrop={onDrop}
                onDragOver={onDragOver}
                onDragLeave={onDragLeave}
                onClick={() => document.getElementById("file-input")?.click()}
                className={`
                  relative rounded-3xl p-10 sm:p-14 text-center cursor-pointer
                  border-2 border-dashed transition-all duration-300 ease-out dropzone-box
                  ${isRtl ? "font-arabic" : ""}
                  ${drag ? "scale-[1.02] border-[var(--accent)] bg-[var(--dropzone-active)] drag-active" : ""}
                  ${file && !drag ? "border-[var(--accent)] bg-[var(--dropzone-active)] has-file" : ""}
                  ${!file && !drag ? "border-[var(--dropzone-border)] bg-[var(--dropzone-bg)] hover:border-[var(--accent)]/30" : ""}
                `}
              >
                <input
                  id="file-input"
                  type="file"
                  accept=".pdf,image/*"
                  className="sr-only"
                  onChange={(e) => setFile(e.target.files?.[0] ?? null)}
                />
                {file ? (
                  <div className="flex flex-col items-center gap-4">
                    <span className="flex h-16 w-16 items-center justify-center rounded-full bg-[var(--accent)]/15 text-[var(--accent)] ring-4 ring-[var(--accent)]/10" aria-hidden>
                      <svg className="h-8 w-8" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
                    </span>
                    <p className={`${isRtl ? "font-arabic" : ""} font-semibold text-[var(--text)] text-lg`}>{t.selectedFile}</p>
                    <p className={`${isRtl ? "font-arabic" : ""} text-sm text-[var(--text-muted)] truncate max-w-full px-2`}>{file.name}</p>
                  </div>
                ) : (
                  <>
                    <span className="mx-auto mb-5 flex h-20 w-20 items-center justify-center rounded-3xl bg-gradient-to-br from-[var(--accent)]/10 to-[var(--accent)]/5 text-[var(--accent)] ring-2 ring-[var(--accent)]/10 transition-all duration-300" aria-hidden>
                      <svg className="h-10 w-10" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" /></svg>
                    </span>
                    <p className={`${isRtl ? "font-arabic" : ""} text-[var(--text)] font-semibold text-lg sm:text-xl`}>{t.dropHint}</p>
                    <p className={`${isRtl ? "font-arabic" : ""} text-sm text-[var(--text-muted)] mt-2`}>{t.dropTypes}</p>
                  </>
                )}
              </div>

              <div className="grid sm:grid-cols-2 gap-4">
                <label className="block">
                  <span className={`text-sm font-medium text-[var(--text-muted)] mb-2 block ${isRtl ? "font-arabic" : ""}`}>{t.responseLanguage}</span>
                  <CustomSelect
                    value={language}
                    options={[
                      { value: "de", label: t.langDe },
                      { value: "ar", label: t.langAr },
                    ]}
                    onChange={(v) => setLanguage(v as "de" | "ar")}
                    isRtl={isRtl}
                    useArabicFont
                    aria-label={t.responseLanguage}
                  />
                </label>
                <label className="block">
                  <span className={`text-sm font-medium text-[var(--text-muted)] mb-2 block ${isRtl ? "font-arabic" : ""}`}>{t.mode}</span>
                  <CustomSelect
                    value={mode}
                    options={[
                      { value: "summary", label: t.modeSummary },
                      { value: "legal_advice", label: t.modeLegal },
                    ]}
                    onChange={(v) => setMode(v as "summary" | "legal_advice")}
                    isRtl={isRtl}
                    aria-label={t.mode}
                  />
                </label>
              </div>

              <button
                type="submit"
                disabled={!file || loading}
                className={`w-full py-3.5 rounded-xl ${isRtl ? "font-arabic" : "font-display"} font-semibold text-base bg-[var(--accent)] text-white dark:text-[var(--bg)] hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed transition-opacity`}
              >
                {loading ? t.processing : t.submit}
              </button>
            </form>

            {loading && (
              <div className="mt-4 h-1.5 rounded-full bg-[var(--border)] overflow-hidden">
                <div
                  className="h-full bg-[var(--accent)] rounded-full transition-all duration-300"
                  style={{ width: `${uploadPercent}%` }}
                />
              </div>
            )}

            {error && (
              <p className="mt-4 text-red-600 dark:text-red-400 text-sm animate-fade-in" role="alert">
                {error}
              </p>
            )}
          </div>
        </div>

        {result && (
          <section className={`mt-16 sm:mt-20 animate-fade-up ${language === "ar" || isRtl ? "font-arabic" : ""}`} aria-label={t.summary}>
            <div className="grid md:grid-cols-2 gap-5 sm:gap-6 lg:gap-8">
              {result.original_text && (
                <ResultCard title={t.originalText} delay="0ms" useArabicFont={isRtl || language === "ar"}>
                  <p className="whitespace-pre-wrap text-[var(--text-muted)] text-sm leading-relaxed">{result.original_text}</p>
                </ResultCard>
              )}
              {result.summary && (
                <ResultCard title={t.summary} delay="60ms" useArabicFont={isRtl || language === "ar"}>
                  <p className="whitespace-pre-wrap text-[var(--text-muted)] text-sm leading-relaxed" dir={language === "ar" ? "rtl" : "ltr"}>{result.summary}</p>
                </ResultCard>
              )}
              {result.legal_recommendation && (
                <ResultCard title={t.recommendation} delay="120ms" useArabicFont={isRtl || language === "ar"}>
                  <p className="whitespace-pre-wrap text-[var(--text-muted)] text-sm leading-relaxed" dir={language === "ar" ? "rtl" : "ltr"}>{result.legal_recommendation}</p>
                </ResultCard>
              )}
              {result.used_paragraphs && result.used_paragraphs.length > 0 && (
                <ResultCard title={t.usedParagraphs} delay="180ms" className="md:col-span-2" useArabicFont={isRtl || language === "ar"}>
                  <ul className="list-disc list-inside space-y-2 text-[var(--text-muted)] text-sm">
                    {result.used_paragraphs.map((p, i) => (
                      <li key={i}>{p}</li>
                    ))}
                  </ul>
                </ResultCard>
              )}
            </div>
            {result.disclaimer && (
              <p className="mt-6 text-xs text-[var(--text-muted)] max-w-2xl">
                {result.disclaimer}
              </p>
            )}
          </section>
        )}

        <Footer
          developedLabel={t.footerDeveloped}
          developedTextFull={t.footerDevelopedFull || undefined}
          websiteLabel={t.footerWebsite}
          emailLabel={t.footerEmail}
          githubLabel={t.footerGitHub}
          linkedinLabel={t.footerLinkedIn}
          isRtl={isRtl}
        />
      </main>
    </div>
  );
}