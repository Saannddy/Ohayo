import { Plus, X } from "lucide-react";
import { useAppStore } from "../../store/appStore";

export function HeadersTab() {
  const { headers, addHeader, updateHeader, removeHeader } = useAppStore();

  return (
    <div className="flex flex-col gap-2 py-3">
      {/* Column labels */}
      {headers.length > 0 && (
        <div className="grid grid-cols-[1fr_1fr_auto] gap-2 px-1">
          <span className="text-[10px] font-semibold text-text-muted uppercase tracking-wide">Key</span>
          <span className="text-[10px] font-semibold text-text-muted uppercase tracking-wide">Value</span>
          <span className="w-7" />
        </div>
      )}

      {/* Header rows */}
      <div className="flex flex-col gap-1.5 max-h-28 overflow-y-auto">
        {headers.map((h) => (
          <div key={h.id} className="grid grid-cols-[1fr_1fr_auto] gap-2 items-center animate-float-in">
            <input
              type="text"
              value={h.key}
              onChange={(e) => updateHeader(h.id, "key", e.target.value)}
              placeholder="Authorization"
              className="input-base py-1.5 text-xs"
            />
            <input
              type="text"
              value={h.value}
              onChange={(e) => updateHeader(h.id, "value", e.target.value)}
              placeholder="Bearer token…"
              className="input-base py-1.5 text-xs"
            />
            <button
              onClick={() => removeHeader(h.id)}
              className="w-7 h-7 flex items-center justify-center rounded-lg bg-danger/10 border border-danger/20 text-danger hover:bg-danger/20 transition-colors flex-shrink-0"
            >
              <X size={12} />
            </button>
          </div>
        ))}
      </div>

      {/* Add button */}
      <div className="flex items-center gap-3 pt-1">
        <button
          onClick={addHeader}
          className="btn-secondary"
        >
          <Plus size={12} />
          Add Header
        </button>
        {headers.length > 0 && (
          <span className="text-xs text-accent">
            {headers.filter((h) => h.key.trim()).length} header{headers.filter((h) => h.key.trim()).length !== 1 ? "s" : ""}
          </span>
        )}
      </div>
    </div>
  );
}
