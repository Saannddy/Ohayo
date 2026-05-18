import { Trash2 } from "lucide-react";
import type { Profile } from "../types";

interface Props {
  name: string;
  profile: Profile;
  onApply: (name: string) => void;
  onDelete: (name: string) => void;
}

export function ProfileItem({ name, profile, onApply, onDelete }: Props) {
  const modeLabel =
    profile.mode === "single" ? "once"
    : profile.mode === "count" ? `×${profile.count || "?"}`
    : `every ${profile.interval || "?"}s`;

  return (
    <button
      onClick={() => onApply(name)}
      className="group w-full text-left bg-card-hover/30 hover:bg-card-hover border border-border/50 hover:border-accent/30 rounded-xl px-3 py-2.5 transition-all"
    >
      <div className="flex items-center gap-2">
        <span className="text-accent text-[10px]">▶</span>
        <span className="text-sm font-medium text-text-primary truncate flex-1">{name}</span>
        <button
          onClick={(e) => { e.stopPropagation(); onDelete(name); }}
          className="opacity-0 group-hover:opacity-100 w-6 h-6 flex items-center justify-center rounded-md text-text-muted hover:text-danger hover:bg-danger/10 transition-all"
        >
          <Trash2 size={11} />
        </button>
      </div>
      <div className="mt-0.5 ml-4 text-[10px] text-text-muted">
        <span className={`font-medium ${profile.method === "GET" ? "text-emerald-400" : profile.method === "POST" ? "text-blue-400" : "text-text-secondary"}`}>
          {profile.method}
        </span>
        {" · "}
        {modeLabel}
      </div>
    </button>
  );
}
