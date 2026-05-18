import { useState } from "react";
import { SendModeTab } from "./tabs/SendModeTab";
import { HeadersTab } from "./tabs/HeadersTab";
import { BodyTab } from "./tabs/BodyTab";
import { useAppStore } from "../store/appStore";

type TabKey = "mode" | "headers" | "body";

const TABS: { key: TabKey; label: string }[] = [
  { key: "mode",    label: "⚡ Send Mode" },
  { key: "headers", label: "≡ Headers"   },
  { key: "body",    label: "{ } Body"    },
];

export function Tabs() {
  const [active, setActive] = useState<TabKey>("mode");
  const { headers } = useAppStore();
  const activeHeaders = headers.filter((h) => h.key.trim()).length;

  return (
    <div className="glass-card overflow-hidden">
      {/* Tab bar */}
      <div className="flex items-center gap-1 px-4 pt-3 pb-0 border-b border-border">
        {TABS.map(({ key, label }) => {
          const isActive = active === key;
          return (
            <button
              key={key}
              onClick={() => setActive(key)}
              className={`relative px-3 pb-2.5 pt-1 text-xs font-semibold transition-all
                ${isActive ? "text-accent" : "text-text-muted hover:text-text-secondary"}`}
            >
              {label}
              {key === "headers" && activeHeaders > 0 && (
                <span className="ml-1 px-1 py-0.5 rounded text-[9px] bg-accent/20 text-accent">{activeHeaders}</span>
              )}
              {isActive && (
                <span className="absolute bottom-0 left-0 right-0 h-0.5 bg-accent rounded-t-full" />
              )}
            </button>
          );
        })}
      </div>

      {/* Tab content */}
      <div className="px-4">
        {active === "mode"    && <SendModeTab />}
        {active === "headers" && <HeadersTab />}
        {active === "body"    && <BodyTab />}
      </div>
    </div>
  );
}
