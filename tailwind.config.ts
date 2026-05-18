import type { Config } from "tailwindcss";

export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        bg: "#060C18",
        surface: "#0B1628",
        card: "#0F1E35",
        "card-hover": "#132440",
        border: { DEFAULT: "#1A3158", subtle: "#0F2040" },
        accent: { DEFAULT: "#F59E0B", hover: "#FBB040", dim: "rgba(245,158,11,0.15)" },
        indigo: { DEFAULT: "#818CF8" },
        success: { DEFAULT: "#34D399", dim: "rgba(52,211,153,0.12)" },
        danger: { DEFAULT: "#F87171", dim: "rgba(248,113,113,0.12)" },
        warning: "#FBBF24",
        "text-primary": "#E2E8F0",
        "text-secondary": "#94A3B8",
        "text-muted": "#475569",
        input: { bg: "#080E1C", border: "#1A3158" },
        log: { bg: "#050810" },
        sidebar: "#070D1C",
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
        mono: ["JetBrains Mono", "Fira Code", "Consolas", "monospace"],
      },
      animation: {
        "pulse-slow": "pulse 3s cubic-bezier(0.4,0,0.6,1) infinite",
        "twinkle": "twinkle 4s ease-in-out infinite",
        "float-in": "floatIn 0.25s ease-out",
        "glow-pulse": "glowPulse 2s ease-in-out infinite",
      },
      keyframes: {
        twinkle: { "0%,100%": { opacity: "0.2" }, "50%": { opacity: "1" } },
        floatIn: { "0%": { opacity: "0", transform: "translateY(6px)" }, "100%": { opacity: "1", transform: "translateY(0)" } },
        glowPulse: { "0%,100%": { boxShadow: "0 0 8px rgba(245,158,11,0.3)" }, "50%": { boxShadow: "0 0 20px rgba(245,158,11,0.6)" } },
      },
      boxShadow: {
        "glow-accent": "0 0 20px rgba(245,158,11,0.12)",
        "glow-success": "0 0 16px rgba(52,211,153,0.1)",
        card: "0 4px 24px rgba(0,0,0,0.5)",
        "card-hover": "0 8px 32px rgba(0,0,0,0.6)",
      },
    },
  },
  plugins: [],
} satisfies Config;
