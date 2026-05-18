import type { Config } from "tailwindcss";

export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        // All colors driven by CSS variables — see index.css for dark/light values
        bg:           "rgb(var(--bg)    / <alpha-value>)",
        surface:      "rgb(var(--sur)   / <alpha-value>)",
        card:         "rgb(var(--card)  / <alpha-value>)",
        "card-hover": "rgb(var(--cardh) / <alpha-value>)",
        border: {
          DEFAULT: "rgb(var(--bdr)  / <alpha-value>)",
          subtle:  "rgb(var(--bdrs) / <alpha-value>)",
        },
        accent: {
          DEFAULT: "rgb(var(--acc)  / <alpha-value>)",
          hover:   "rgb(var(--acch) / <alpha-value>)",
        },
        success: "rgb(var(--suc) / <alpha-value>)",
        danger:  "rgb(var(--dan) / <alpha-value>)",
        warning: "rgb(var(--wrn) / <alpha-value>)",
        "text-primary":   "rgb(var(--tp)  / <alpha-value>)",
        "text-secondary": "rgb(var(--ts)  / <alpha-value>)",
        "text-muted":     "rgb(var(--tm)  / <alpha-value>)",
        input: {
          bg:     "rgb(var(--ibg) / <alpha-value>)",
          border: "rgb(var(--ibd) / <alpha-value>)",
        },
        log:     { bg: "rgb(var(--lbg) / <alpha-value>)" },
        sidebar: "rgb(var(--sb)  / <alpha-value>)",
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
        mono: ["JetBrains Mono", "Fira Code", "Consolas", "monospace"],
      },
      animation: {
        "pulse-slow":  "pulse 3s cubic-bezier(0.4,0,0.6,1) infinite",
        "twinkle":     "twinkle 4s ease-in-out infinite",
        "float-in":    "floatIn 0.25s ease-out",
        "ember":       "ember 0.45s ease-in-out infinite alternate",
        "morning-orb": "morningOrb 6s ease-in-out infinite",
      },
      keyframes: {
        twinkle:    { "0%,100%": { opacity: "0.15" }, "50%": { opacity: "1" } },
        floatIn:    { "0%": { opacity:"0", transform:"translateY(6px)" }, "100%": { opacity:"1", transform:"translateY(0)" } },
        ember: {
          "0%":   { boxShadow: "0 0 4px 2px #FFB200, 0 0 8px 4px #FF6B00, 0 0 14px 6px rgba(255,60,0,0.5)", transform:"translateY(-50%) scale(1)" },
          "100%": { boxShadow: "0 0 6px 3px #FFD000, 0 0 12px 6px #FF8C00, 0 0 20px 8px rgba(255,80,0,0.7)", transform:"translateY(-50%) scale(1.25)" },
        },
        morningOrb: {
          "0%,100%": { transform:"translateY(0) scale(1)", opacity:"0.06" },
          "50%":     { transform:"translateY(-12px) scale(1.1)", opacity:"0.12" },
        },
      },
      boxShadow: {
        "glow-acc":     "0 0 20px rgb(var(--acc)/0.15)",
        "glow-success": "0 0 16px rgb(var(--suc)/0.12)",
        card:           "0 4px 24px rgba(0,0,0,0.45)",
        "card-hover":   "0 8px 32px rgba(0,0,0,0.55)",
      },
    },
  },
  plugins: [],
} satisfies Config;
