import { useAppStore } from "../../store/appStore";
import type { ScheduleMode } from "../../types";

interface ModeCard { value: ScheduleMode; label: string; icon: string; tip: string; }

const MODES: ModeCard[] = [
  { value: "single",     label: "Once",       icon: "⚡", tip: "Fire a single request" },
  { value: "count",      label: "Repeat N",   icon: "🔁", tip: "Send N times with interval" },
  { value: "continuous", label: "Continuous", icon: "♾",  tip: "Send until stop time" },
];

export function SendModeTab() {
  const { mode, interval, count, stopTime, setMode, setInterval, setCount, setStopTime } = useAppStore();

  return (
    <div className="flex flex-col gap-3 py-3">
      {/* Mode cards */}
      <div className="grid grid-cols-3 gap-2">
        {MODES.map(({ value, label, icon, tip }) => {
          const active = mode === value;
          return (
            <button
              key={value}
              onClick={() => setMode(value)}
              className={`flex flex-col items-center gap-1 py-3 px-2 rounded-xl border text-center
                transition-all duration-200 ${active
                  ? "bg-accent/10 border-accent text-accent shadow-glow-acc"
                  : "bg-surface border-border text-text-secondary hover:border-border hover:text-text-primary hover:bg-card-hover"
                }`}
            >
              <span className="text-xl">{icon}</span>
              <span className="text-sm font-semibold">{label}</span>
              <span className="text-[10px] text-text-muted leading-tight">{tip}</span>
            </button>
          );
        })}
      </div>

      {/* Dynamic fields */}
      {mode !== "single" && (
        <div className="grid grid-cols-2 gap-3">
          {/* Interval — always shown for non-single */}
          <div>
            <label className="block text-xs font-semibold text-text-secondary mb-1.5 uppercase tracking-wide">
              Every (seconds)
            </label>
            <input
              type="number"
              min="1"
              value={interval}
              onChange={(e) => setInterval(e.target.value)}
              placeholder="5"
              className="input-base"
            />
          </div>

          {mode === "count" ? (
            <div>
              <label className="block text-xs font-semibold text-text-secondary mb-1.5 uppercase tracking-wide">
                Count (N)
              </label>
              <input
                type="number"
                min="1"
                value={count}
                onChange={(e) => setCount(e.target.value)}
                placeholder="10"
                className="input-base"
              />
            </div>
          ) : (
            <div>
              <label className="block text-xs font-semibold text-text-secondary mb-1.5 uppercase tracking-wide">
                Until (HH:MM)
              </label>
              <input
                type="text"
                value={stopTime}
                onChange={(e) => setStopTime(e.target.value)}
                placeholder="23:59"
                className="input-base"
              />
            </div>
          )}
        </div>
      )}
    </div>
  );
}
