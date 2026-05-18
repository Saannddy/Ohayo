import { useAppStore } from "../store/appStore";
import { useScheduler } from "../hooks/useScheduler";
import { StatusDot } from "./StatusDot";
import { METHOD_COLORS, METHOD_BG } from "../theme/tokens";
import type { HttpMethod } from "../types";

const METHODS: HttpMethod[] = ["GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"];

export function RequestBar() {
  const { url, method, isRunning, setUrl, setMethod } = useAppStore();
  const { startScheduler, stopScheduler } = useScheduler();

  const validate = (): string | null => {
    if (!url.trim()) return "Please enter a URL.";
    return null;
  };

  const handleSend = async () => {
    if (isRunning) {
      await stopScheduler();
      return;
    }
    const err = validate();
    if (err) { alert(err); return; }
    try { await startScheduler(); }
    catch (e) { alert(String(e)); }
  };

  return (
    <div className="glass-card p-3">
      <div className="flex items-center gap-2">
        {/* Method selector */}
        <div className="relative flex-shrink-0">
          <select
            value={method}
            onChange={(e) => setMethod(e.target.value as HttpMethod)}
            disabled={isRunning}
            className={`
              appearance-none cursor-pointer font-bold text-sm h-11 pl-3 pr-6 rounded-lg
              bg-input-bg border border-input-border focus:outline-none focus:border-accent/60
              transition-colors disabled:opacity-60 disabled:cursor-not-allowed
              ${METHOD_COLORS[method] ?? "text-text-primary"}
              ${METHOD_BG[method] ?? ""}
            `}
          >
            {METHODS.map((m) => (
              <option key={m} value={m} className="bg-card text-text-primary">{m}</option>
            ))}
          </select>
          <span className="pointer-events-none absolute right-2 top-1/2 -translate-y-1/2 text-text-muted text-xs">▾</span>
        </div>

        {/* URL input */}
        <input
          type="text"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && !isRunning && handleSend()}
          placeholder="https://api.example.com/ping"
          disabled={isRunning}
          className="input-base h-11 flex-1 disabled:opacity-60 disabled:cursor-not-allowed"
        />

        {/* Status dot */}
        <StatusDot />

        {/* Send / Stop button */}
        <button
          onClick={handleSend}
          className={`
            flex-shrink-0 h-11 px-6 rounded-lg font-semibold text-sm transition-all duration-200
            ${isRunning
              ? "bg-danger hover:bg-danger/90 text-white shadow-none"
              : "bg-accent hover:bg-accent-hover text-bg shadow-glow-acc"
            }
          `}
        >
          {isRunning ? "⏹  Stop" : "▶  Send"}
        </button>
      </div>
    </div>
  );
}
