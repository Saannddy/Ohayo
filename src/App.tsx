import { useEffect } from "react";
import { StarField } from "./components/StarField";
import { Sidebar } from "./components/Sidebar";
import { RequestBar } from "./components/RequestBar";
import { Tabs } from "./components/Tabs";
import { LogPanel } from "./components/LogPanel";
import { useScheduler } from "./hooks/useScheduler";
import { useTheme } from "./hooks/useTheme";

export function App() {
  const { setupListeners } = useScheduler();
  useTheme();

  useEffect(() => {
    const cleanup = setupListeners();
    return cleanup;
  }, [setupListeners]);

  return (
    <div className="flex h-screen bg-bg text-text-primary font-sans overflow-hidden select-none">
      <Sidebar />

      <div className="flex-1 relative min-w-0 overflow-hidden">
        <StarField />

        <div className="absolute inset-0 flex flex-col gap-3 p-4 overflow-hidden z-10">
          {/* Top bar */}
          <div className="flex items-baseline gap-3 flex-shrink-0">
            <h1 className="text-xl font-bold tracking-tight text-text-primary">
              Wake Up API
            </h1>
            <span className="text-xs text-text-muted">
              Schedule HTTP requests
            </span>
          </div>

          {/* Request bar */}
          <div className="flex-shrink-0">
            <RequestBar />
          </div>

          {/* Tabs */}
          <div className="flex-shrink-0">
            <Tabs />
          </div>

          {/* Log panel — fills remaining space */}
          <div className="flex-1 min-h-0">
            <LogPanel />
          </div>
        </div>
      </div>
    </div>
  );
}
