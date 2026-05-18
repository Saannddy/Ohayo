import { Download, Trash2 } from "lucide-react";
import { useAppStore } from "../store/appStore";
import { StatusDot } from "./StatusDot";

export function LogHeader() {
  const { logEntries, statusMessage, statusColor, clearLog } = useAppStore();

  const exportLog = () => {
    if (!logEntries.length) return;
    const lines = logEntries.map((e) => {
      if (e.tag === "error") {
        return `[${e.timestamp}]  #${String(e.count).padStart(4, " ")}  ERROR    —  ${e.elapsedMs.toFixed(1).padStart(8)} ms  ${e.error}`;
      }
      return `[${e.timestamp}]  #${String(e.count).padStart(4, " ")}  ${e.method.padEnd(7)}  ${e.status}  ${e.elapsedMs.toFixed(1).padStart(8)} ms`;
    });
    const blob = new Blob([lines.join("\n")], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `ohayo-log-${new Date().toISOString().slice(0, 10)}.txt`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const statusTextColor =
    statusColor === "success" ? "text-success"
    : statusColor === "danger" ? "text-danger"
    : "text-text-muted";

  return (
    <div className="flex items-center gap-3">
      <span className="text-base font-bold text-text-primary">Response Log</span>

      <div className="flex items-center gap-2">
        <StatusDot />
        <span className={`text-xs ${statusTextColor} transition-colors`}>{statusMessage}</span>
      </div>

      <div className="ml-auto flex items-center gap-2">
        <button onClick={exportLog} disabled={!logEntries.length} className="btn-secondary disabled:opacity-30 disabled:cursor-not-allowed">
          <Download size={12} />
          Export
        </button>
        <button onClick={clearLog} className="btn-secondary">
          <Trash2 size={12} />
          Clear
        </button>
      </div>
    </div>
  );
}
