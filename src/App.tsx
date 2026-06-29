import { useEffect } from "react";
import { StarField } from "./components/StarField";
import { Sidebar } from "./components/Sidebar";
import { TopNav } from "./components/TopNav";
import { RequestTitle } from "./components/RequestTitle";
import { RequestBar } from "./components/RequestBar";
import { Tabs } from "./components/Tabs";
import { LogPanel } from "./components/LogPanel";
import { LogsPage } from "./components/LogsPage";
import { EnvironmentsPage } from "./components/EnvironmentsPage";
import { useScheduler } from "./hooks/useScheduler";
import { useTheme } from "./hooks/useTheme";
import { useAppStore } from "./store/appStore";

export function App() {
  const { setupListeners } = useScheduler();
  const page = useAppStore((s) => s.page);
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
          <TopNav />

          {page === "request" && (
            <>
              <div className="flex-shrink-0"><RequestTitle /></div>
              <div className="flex-shrink-0"><RequestBar /></div>
              <div className="flex-shrink-0"><Tabs /></div>
              <div className="flex-1 min-h-0"><LogPanel /></div>
            </>
          )}

          {page === "logs" && <LogsPage />}

          {page === "environments" && <EnvironmentsPage />}
        </div>
      </div>
    </div>
  );
}
