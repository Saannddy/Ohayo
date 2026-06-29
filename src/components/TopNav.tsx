import { useState } from "react";
import { Save, Send, ScrollText, Layers3 } from "lucide-react";
import { useAppStore } from "../store/appStore";
import { useCollections } from "../hooks/useCollections";
import { EnvSelector } from "./EnvSelector";
import { Modal } from "./Modal";
import type { Page } from "../types";

const TABS: { id: Page; label: string; icon: typeof Send }[] = [
  { id: "request", label: "Request", icon: Send },
  { id: "logs", label: "Logs", icon: ScrollText },
  { id: "environments", label: "Environments", icon: Layers3 },
];

export function TopNav() {
  const { page, setPage, collectionRoot, activeRequestPath } = useAppStore();
  const { saveRequest, saveActive } = useCollections();
  const [saving, setSaving] = useState(false);
  const [name, setName] = useState("");

  const handleSave = async () => {
    if (!collectionRoot) return;
    // Open request → save in place. Otherwise prompt for a name.
    if (activeRequestPath) {
      await saveActive();
      return;
    }
    setName("");
    setSaving(true);
  };

  const confirmSave = async () => {
    const n = name.trim();
    if (!n) return;
    await saveRequest(n);
    setSaving(false);
    setName("");
  };

  return (
    <div className="flex items-center justify-between gap-3 flex-shrink-0">
      {/* Page tabs */}
      <div className="flex items-center gap-1 bg-input-bg/60 border border-border/50 rounded-xl p-1">
        {TABS.map(({ id, label, icon: Icon }) => (
          <button
            key={id}
            onClick={() => setPage(id)}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
              page === id
                ? "bg-accent text-bg shadow-glow-acc"
                : "text-text-muted hover:text-text-primary hover:bg-card-hover/60"
            }`}
          >
            <Icon size={13} />
            {label}
          </button>
        ))}
      </div>

      {/* Right cluster */}
      <div className="flex items-center gap-2">
        <EnvSelector />
        <button
          onClick={handleSave}
          disabled={!collectionRoot}
          title={collectionRoot ? "Save current request" : "Open a collection first"}
          className="inline-flex items-center gap-1.5 h-9 px-3 rounded-lg text-xs font-semibold
                     bg-surface border border-border text-text-secondary hover:text-text-primary
                     hover:border-accent/40 transition-all disabled:opacity-40 disabled:cursor-not-allowed"
        >
          <Save size={13} />
          Save Current
        </button>
      </div>

      <Modal
        open={saving}
        title="Save request"
        onClose={() => setSaving(false)}
        footer={
          <>
            <button onClick={() => setSaving(false)} className="btn-secondary px-3 py-1.5">Cancel</button>
            <button onClick={confirmSave} className="px-3 py-1.5 rounded-lg bg-accent text-bg text-xs font-bold">Save</button>
          </>
        }
      >
        <p className="mb-2 text-text-muted text-xs">Saved as a <code>.ohy</code> file in the collection.</p>
        <input
          autoFocus
          value={name}
          onChange={(e) => setName(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && confirmSave()}
          placeholder="Request name…"
          className="input-base w-full py-2 text-sm"
        />
      </Modal>
    </div>
  );
}
