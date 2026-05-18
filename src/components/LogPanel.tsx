import { useAppStore } from "../store/appStore";
import { LogHeader } from "./LogHeader";
import { StatsRow } from "./StatsRow";
import { LogEntries } from "./LogEntries";

export function LogPanel() {
  const { progress, isRunning } = useAppStore();
  const pct = Math.round(progress * 100);

  return (
    <div className="glass-card flex flex-col h-full overflow-hidden">

      {/* ── Burning rope progress bar ── */}
      <div className="rope-track">
        {pct > 0 && (
          <div className="rope-bar" style={{ width: `${pct}%` }}>
            {/* Glowing ember at the burning tip */}
            {isRunning && pct < 99 && <span className="rope-ember" />}
          </div>
        )}
      </div>

      <div className="flex flex-col gap-3 p-4 flex-1 min-h-0">
        <LogHeader />
        <StatsRow />
        <LogEntries />
      </div>
    </div>
  );
}
