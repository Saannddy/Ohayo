import { useMemo } from "react";
import { Trash2 } from "lucide-react";
import { useAppStore } from "../store/appStore";
import { TAG_COLORS } from "../theme/tokens";
import type { LogEntry } from "../types";

function pretty(body: string): string {
  try { return JSON.stringify(JSON.parse(body), null, 2); }
  catch { return body; }
}

export function LogsPage() {
  const { logEntries, selectedLogId, setSelectedLogId, clearLog } = useAppStore();

  const selected = useMemo(
    () => logEntries.find((e) => e.id === selectedLogId) ?? null,
    [logEntries, selectedLogId],
  );

  return (
    <div className="glass-card flex-1 flex min-h-0 overflow-hidden">
      {/* List */}
      <div className="w-72 flex-shrink-0 border-r border-border/50 flex flex-col">
        <div className="px-3 py-2.5 flex items-center justify-between border-b border-border/50">
          <span className="text-[10px] font-bold text-text-muted uppercase tracking-widest">
            Responses · {logEntries.length}
          </span>
          <button onClick={clearLog} title="Clear log" className="text-text-muted hover:text-danger"><Trash2 size={13} /></button>
        </div>
        <div className="flex-1 overflow-y-auto p-2 flex flex-col gap-1">
          {logEntries.length === 0 && <p className="text-xs text-text-muted px-2 mt-2">No responses yet.</p>}
          {[...logEntries].reverse().map((e) => (
            <Row key={e.id} entry={e} active={e.id === selectedLogId} onClick={() => setSelectedLogId(e.id)} />
          ))}
        </div>
      </div>

      {/* Detail */}
      <div className="flex-1 flex flex-col min-w-0">
        {!selected ? (
          <div className="flex-1 flex items-center justify-center text-text-muted text-sm">Select a response to inspect.</div>
        ) : (
          <Detail entry={selected} />
        )}
      </div>
    </div>
  );
}

function Row({ entry, active, onClick }: { entry: LogEntry; active: boolean; onClick: () => void }) {
  const color = TAG_COLORS[entry.tag];
  return (
    <button
      onClick={onClick}
      className={`flex items-center gap-2 px-2.5 py-2 rounded-lg text-left text-xs font-mono transition-all ${
        active ? "bg-card-hover border border-accent/40" : "border border-transparent hover:bg-card-hover/60"
      }`}
    >
      <span className="text-text-muted">#{entry.count}</span>
      <span className="font-bold" style={{ color }}>{entry.error ? "ERR" : entry.status}</span>
      <span className="text-text-secondary truncate flex-1">{entry.method}</span>
      <span className="text-text-muted">{Math.round(entry.elapsedMs)}ms</span>
    </button>
  );
}

function Detail({ entry }: { entry: LogEntry }) {
  const color = TAG_COLORS[entry.tag];
  return (
    <div className="flex-1 overflow-y-auto p-4 flex flex-col gap-4">
      {/* Summary */}
      <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-xs">
        <span className="font-bold text-sm" style={{ color }}>{entry.error ? "ERROR" : entry.status}</span>
        <span className="text-text-secondary font-mono">{entry.method}</span>
        <span className="text-text-muted">{Math.round(entry.elapsedMs)} ms</span>
        <span className="text-text-muted">{entry.timestamp}</span>
        <span className="text-text-muted">#{entry.count}</span>
      </div>
      {entry.url && <div className="text-xs text-text-secondary break-all font-mono">{entry.url}</div>}

      {entry.error && (
        <Section title="Error">
          <pre className="text-xs text-danger whitespace-pre-wrap break-all">{entry.error}</pre>
        </Section>
      )}

      {entry.headers && Object.keys(entry.headers).length > 0 && (
        <Section title="Response headers">
          <div className="grid grid-cols-[auto,1fr] gap-x-4 gap-y-0.5 text-[11px] font-mono">
            {Object.entries(entry.headers).map(([k, v]) => (
              <div key={k} className="contents">
                <span className="text-accent">{k}</span>
                <span className="text-text-secondary break-all">{v}</span>
              </div>
            ))}
          </div>
        </Section>
      )}

      {entry.body !== undefined && (
        <Section title="Response body">
          {entry.body ? (
            <pre className="text-[11px] font-mono text-text-secondary whitespace-pre-wrap break-all bg-input-bg/50 rounded-lg p-3 max-h-[50vh] overflow-auto">
              {pretty(entry.body)}
            </pre>
          ) : (
            <p className="text-xs text-text-muted italic">Empty body.</p>
          )}
        </Section>
      )}
    </div>
  );
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="flex flex-col gap-1.5">
      <span className="text-[10px] font-bold text-text-muted uppercase tracking-widest">{title}</span>
      {children}
    </div>
  );
}
