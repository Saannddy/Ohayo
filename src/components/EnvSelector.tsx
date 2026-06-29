import { Layers } from "lucide-react";
import { useAppStore } from "../store/appStore";

export function EnvSelector() {
  const { environments, activeEnvName, setActiveEnvName } = useAppStore();

  return (
    <div className="relative flex items-center">
      <Layers size={13} className="absolute left-2.5 text-text-muted pointer-events-none" />
      <select
        value={activeEnvName ?? ""}
        onChange={(e) => setActiveEnvName(e.target.value || null)}
        className="appearance-none cursor-pointer text-xs h-9 pl-8 pr-7 rounded-lg bg-input-bg
                   border border-input-border text-text-secondary focus:outline-none
                   focus:border-accent/60 transition-colors"
        title="Active environment"
      >
        <option value="">No environment</option>
        {environments.map((e) => (
          <option key={e.name} value={e.name} className="bg-card text-text-primary">{e.name}</option>
        ))}
      </select>
      <span className="pointer-events-none absolute right-2 text-text-muted text-xs">▾</span>
    </div>
  );
}
