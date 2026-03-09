import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: "class", // .dark on html toggled by ThemeToggle
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        display: ["var(--font-syne)", "system-ui", "sans-serif"],
        body: ["var(--font-outfit)", "system-ui", "sans-serif"],
        arabic: ["var(--font-cairo)", "system-ui", "sans-serif"], // used when uiLocale === "ar"
      },
      colors: {
        ink: {
          950: "var(--text)",
          900: "var(--bg-elevated)",
          800: "var(--surface)",
          700: "var(--surface-hover)",
          600: "var(--text-muted)",
          500: "var(--text-muted)",
        },
        accent: {
          DEFAULT: "var(--accent)",
          light: "var(--accent-hover)",
          dark: "var(--accent-hover)",
        },
        paper: "var(--bg)",
        cream: "var(--text)",
      },
      animation: {
        "fade-up": "fadeUp 0.55s cubic-bezier(0.22, 1, 0.36, 1) forwards",
        "fade-in": "fadeIn 0.4s ease-out forwards",
      },
      keyframes: {
        fadeUp: {
          "0%": { opacity: "0", transform: "translateY(16px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        fadeIn: {
          "0%": { opacity: "0" },
          "100%": { opacity: "1" },
        },
      },
    },
  },
  plugins: [],
};

export default config;
