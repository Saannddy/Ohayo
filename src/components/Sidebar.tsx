import { useState, useEffect } from "react";
import { BookmarkPlus, Sun, Moon } from "lucide-react";
import { useProfiles } from "../hooks/useProfiles";
import { useTheme } from "../hooks/useTheme";
import { ProfileItem } from "./ProfileItem";

export function Sidebar() {
  const { profiles, loadProfiles, saveProfile, deleteProfile, applyProfile } = useProfiles();
  const { isDark, toggleTheme } = useTheme();
  const [saving, setSaving] = useState(false);
  const [saveName, setSaveName] = useState("");

  useEffect(() => { loadProfiles(); }, [loadProfiles]);

  const handleSave = async () => {
    if (saving) {
      const name = saveName.trim();
      if (name) { await saveProfile(name); }
      setSaving(false);
      setSaveName("");
    } else {
      setSaving(true);
    }
  };

  return (
    <aside className="w-60 flex-shrink-0 flex flex-col bg-sidebar border-r border-border/50 overflow-hidden">
      {/* Brand */}
      <div className="px-5 pt-5 pb-4 flex-shrink-0">
        <div className="text-2xl font-bold text-gradient-accent tracking-tight">おはよう</div>
        <div className="text-[10px] text-text-muted mt-0.5 tracking-widest uppercase">API Waker · v2</div>
      </div>

      <div className="h-px bg-border/50 mx-4 flex-shrink-0" />

      {/* Collections header */}
      <div className="px-5 pt-4 pb-2 flex-shrink-0">
        <span className="text-[9px] font-bold text-text-muted uppercase tracking-widest">Collections</span>
      </div>

      {/* Profile list */}
      <div className="flex-1 overflow-y-auto px-3 pb-2 flex flex-col gap-1.5 min-h-0">
        {profiles.length === 0 ? (
          <div className="text-center text-text-muted text-xs mt-6 leading-relaxed px-2">
            No collections yet.{"\n"}Save a request to get started.
          </div>
        ) : (
          profiles.map(([name, profile]) => (
            <ProfileItem
              key={name}
              name={name}
              profile={profile}
              onApply={applyProfile}
              onDelete={deleteProfile}
            />
          ))
        )}
      </div>

      <div className="h-px bg-border/50 mx-4 flex-shrink-0" />

      {/* Bottom section */}
      <div className="px-4 py-4 flex flex-col gap-3 flex-shrink-0">
        {/* Save input or save button */}
        {saving ? (
          <div className="flex gap-1.5">
            <input
              autoFocus
              type="text"
              value={saveName}
              onChange={(e) => setSaveName(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleSave()}
              placeholder="Collection name…"
              className="input-base py-1.5 text-xs flex-1"
            />
            <button onClick={handleSave} className="px-3 py-1.5 rounded-lg bg-accent text-bg text-xs font-bold">
              ✓
            </button>
            <button onClick={() => { setSaving(false); setSaveName(""); }} className="px-2.5 py-1.5 rounded-lg bg-surface border border-border text-text-muted text-xs">
              ✕
            </button>
          </div>
        ) : (
          <button onClick={handleSave} className="btn-secondary w-full justify-center">
            <BookmarkPlus size={13} />
            Save Current
          </button>
        )}

        {/* Theme toggle */}
        <div className="flex items-center justify-between">
          <span className="text-xs text-text-muted">{isDark ? "Dark mode" : "Light mode"}</span>
          <button
            onClick={toggleTheme}
            className="w-8 h-8 flex items-center justify-center rounded-lg text-text-muted hover:text-accent hover:bg-surface transition-all"
          >
            {isDark ? <Sun size={15} /> : <Moon size={15} />}
          </button>
        </div>
      </div>
    </aside>
  );
}
