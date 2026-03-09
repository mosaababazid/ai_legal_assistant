import type { Metadata } from "next";
import { Syne, Outfit, Cairo } from "next/font/google";
import "./globals.css";

const syne = Syne({
  subsets: ["latin"],
  variable: "--font-syne",
  display: "swap",
});

const outfit = Outfit({
  subsets: ["latin"],
  variable: "--font-outfit",
  display: "swap",
});

const cairo = Cairo({
  subsets: ["latin", "arabic"],
  variable: "--font-cairo",
  display: "swap",
});

export const metadata: Metadata = {
  title: "Recht & Klar | AI Legal Assistant",
  description: "Document understanding and legal assistance — upload, summarize, get grounded advice.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="de" className={`${syne.variable} ${outfit.variable} ${cairo.variable}`} suppressHydrationWarning>
      <head>
        <script
          dangerouslySetInnerHTML={{
            __html: `(function(){var t=localStorage.getItem('theme');if(!t){t='light';localStorage.setItem('theme','light');}var isDark=t==='dark';document.documentElement.classList.remove('dark');if(isDark)document.documentElement.classList.add('dark');var L=localStorage.getItem('ui-locale');if(L!=='ar'&&L!=='de'){L='de';localStorage.setItem('ui-locale','de');}document.documentElement.setAttribute('data-ui-locale',L);})();`,
          }}
        />
      </head>
      <body className="min-h-screen font-body bg-[var(--bg-elevated)] text-[var(--text)] selection:bg-[var(--accent)]/20">
        {children}
      </body>
    </html>
  );
}