import { useEffect, useState } from "react";
import { FileText } from "lucide-react";
import { useAppStore } from "../store/appStore";
import { useCollections } from "../hooks/useCollections";

/** Editable name of the currently-open request, shown above the request editor. */
export function RequestTitle() {
  const path = useAppStore((s) => s.activeRequestPath);
  const { renameEntry } = useCollections();
  const baseName = path ? (path.split(/[\\/]/).pop() || "").replace(/\.ohy$/, "") : "";
  const [name, setName] = useState(baseName);

  useEffect(() => { setName(baseName); }, [baseName]);

  if (!path) {
    return (
      <div className="text-xs text-text-muted px-1 py-1">
        Unsaved request — hit <span className="text-text-secondary">Save Current</span> to store it.
      </div>
    );
  }

  const commit = async () => {
    const n = name.trim();
    if (n && n !== baseName) await renameEntry(path, n);
    else setName(baseName);
  };

  return (
    <div className="flex items-center gap-2 px-1">
      <FileText size={14} className="text-accent flex-shrink-0" />
      <input
        value={name}
        onChange={(e) => setName(e.target.value)}
        onKeyDown={(e) => { if (e.key === "Enter") (e.target as HTMLInputElement).blur(); }}
        onBlur={commit}
        placeholder="Request name"
        title="Rename this request"
        className="bg-transparent text-base font-semibold text-text-primary px-1.5 py-0.5 rounded-md
                   border border-transparent hover:border-border/60 focus:outline-none
                   focus:bg-input-bg/60 focus:border-accent/40 transition-colors max-w-md min-w-0 flex-1"
      />
    </div>
  );
}
