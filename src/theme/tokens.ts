export const METHOD_COLORS: Record<string, string> = {
  GET:     "text-emerald-400",
  POST:    "text-blue-400",
  PUT:     "text-purple-400",
  PATCH:   "text-amber-400",
  DELETE:  "text-red-400",
  HEAD:    "text-slate-400",
  OPTIONS: "text-slate-400",
};

export const METHOD_BG: Record<string, string> = {
  GET:     "bg-emerald-500/10",
  POST:    "bg-blue-500/10",
  PUT:     "bg-purple-500/10",
  PATCH:   "bg-amber-500/10",
  DELETE:  "bg-red-500/10",
  HEAD:    "bg-slate-500/10",
  OPTIONS: "bg-slate-500/10",
};

export const TAG_COLORS: Record<string, string> = {
  "2xx":   "#34D399",
  "3xx":   "#FBBF24",
  "4xx":   "#F87171",
  "5xx":   "#EF4444",
  "error": "#F43F5E",
};

export const FILTER_LABELS = ["ALL", "2xx", "3xx", "4xx", "5xx", "ERR"] as const;

export const INPUT_CLASS =
  "w-full bg-input-bg border border-input-border rounded-lg px-3 py-2 text-text-primary " +
  "placeholder:text-text-muted text-sm focus:outline-none focus:border-accent/60 " +
  "focus:ring-1 focus:ring-accent/20 transition-colors";

export const CARD_CLASS =
  "bg-card border border-border rounded-xl shadow-card";

export const BTN_SECONDARY =
  "inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium " +
  "bg-surface border border-border text-text-secondary hover:text-text-primary " +
  "hover:border-border hover:bg-card-hover transition-all";
