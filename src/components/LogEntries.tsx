import { useEffect, useRef } from "react";
import { useAppStore } from "../store/appStore";
import { TAG_COLORS, FILTER_LABELS } from "../theme/tokens";
import type { LogFilter, LogEntry } from "../types";

function entryText(e: LogEntry): string {
  if (e.tag === "error") {
    return `[${e.timestamp}]  #${String(e.count).padStart(4, " ")}  ERROR    —  ${e.elapsedMs.toFixed(1).padStart(8)} ms  ${e.error ?? ""}`;
  }
  return `[${e.timestamp}]  #${String(e.count).padStart(4, " ")}  ${(e.method ?? "").padEnd(7)}  ${e.status ?? ""}  ${e.elapsedMs.toFixed(1).padStart(8)} ms`;
}

function entryMatches(e: LogEntry, filter: LogFilter): boolean {
  if (filter === "ALL") return true;
  if (filter === "ERR") return e.tag === "error";
  return e.tag === filter;
}

export function LogEntries() {
  const { logEntries, logFilter, setLogFilter } = useAppStore();
  const bottomRef = useRef<HTMLDivElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  const visible = logEntries.filter((e) => entryMatches(e, logFilter));

  useEffect(() => {
    const el = containerRef.current;
    if (!el) return;
    const isBottom = el.scrollHeight - el.scrollTop - el.clientHeight < 80;
    if (isBottom) bottomRef.current?.scrollIntoView({ behavior: "instant" });
  }, [visible.length]);

  return (
    <div className="flex flex-col gap-2 min-h-0 flex-1">
      {/* Filter pills */}
      <div className="flex items-center gap-1.5 flex-shrink-0">
        {FILTER_LABELS.map((f) => {
          const active = f === logFilter;
          return (
            <button
              key={f}
              onClick={() => setLogFilter(f)}
              className={`px-2.5 py-1 rounded-md text-xs font-semibold transition-all ${
                active
                  ? "bg-accent text-bg"
                  : "bg-surface border border-border text-text-muted hover:text-text-secondary hover:border-border"
              }`}
            >
              {f}
            </button>
          );
        })}
        {visible.length > 0 && (
          <span className="ml-auto text-xs text-text-muted tabular-nums">{visible.length} entries</span>
        )}
      </div>

      {/* Log content */}
      <div
        ref={containerRef}
        className="flex-1 min-h-0 overflow-y-auto bg-log-bg border border-border/50 rounded-xl p-3 font-mono text-[11px] leading-relaxed"
      >
        {visible.length === 0 ? (
          <div className="h-full flex items-center justify-center">
            <span className="text-text-muted text-xs">No log entries yet. Send a request to get started.</span>
          </div>
        ) : (
          visible.map((e) => (
            <div
              key={e.id}
              className="animate-float-in whitespace-pre"
              style={{ color: TAG_COLORS[e.tag] ?? "#94A3B8" }}
            >
              {entryText(e)}
            </div>
          ))
        )}
        <div ref={bottomRef} />
      </div>
    </div>
  );
}
