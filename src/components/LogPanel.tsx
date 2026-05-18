import { useAppStore } from "../store/appStore";
import { LogHeader } from "./LogHeader";
import { StatsRow } from "./StatsRow";
import { LogEntries } from "./LogEntries";

export function LogPanel() {
  const { progress } = useAppStore();

  return (
    <div className="glass-card flex flex-col h-full overflow-hidden">
      {/* Top accent stripe with progress */}
      <div className="h-1 bg-border/50 flex-shrink-0 rounded-t-xl overflow-hidden relative">
        <div
          className="h-full transition-all duration-500 ease-out"
          style={{
            width: `${Math.round(progress * 100)}%`,
            background: "linear-gradient(90deg, #F59E0B, #34D399)",
          }}
        />
      </div>

      <div className="flex flex-col gap-3 p-4 flex-1 min-h-0">
        <LogHeader />
        <StatsRow />
        <LogEntries />
      </div>
    </div>
  );
}
