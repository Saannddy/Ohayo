import { useEffect, useMemo, useState } from "react";
import { Plus, Trash2, Check, Layers3 } from "lucide-react";
import { useAppStore } from "../store/appStore";
import { useCollections } from "../hooks/useCollections";
import { Modal } from "./Modal";
import type { Environment } from "../types";

interface VarRow { id: string; key: string; value: string; }

const toRows = (vars: Record<string, string>): VarRow[] =>
  Object.entries(vars).map(([key, value]) => ({ id: crypto.randomUUID(), key, value }));

export function EnvironmentsPage() {
  const { environments, collectionRoot } = useAppStore();
  const { saveEnvironment, deleteEnvironment } = useCollections();

  const [selected, setSelected] = useState<string | null>(null);
  const [rows, setRows] = useState<VarRow[]>([]);
  const [creating, setCreating] = useState(false);
  const [newName, setNewName] = useState("");
  const [pendingDelete, setPendingDelete] = useState<string | null>(null);

  const active = useMemo(() => environments.find((e) => e.name === selected) ?? null, [environments, selected]);

  // Default selection + load rows when selection/source changes.
  useEffect(() => {
    if (!selected && environments.length) setSelected(environments[0].name);
  }, [environments, selected]);
  useEffect(() => { setRows(active ? toRows(active.vars) : []); }, [active]);

  if (!collectionRoot) {
    return <Empty text="Open a collection to manage environments." />;
  }

  const persist = async (env: Environment) => { await saveEnvironment(env); };

  const saveRows = async () => {
    if (!active) return;
    const vars: Record<string, string> = {};
    rows.forEach((r) => { if (r.key.trim()) vars[r.key.trim()] = r.value; });
    await persist({ name: active.name, vars });
  };

  const createEnv = async () => {
    const n = newName.trim();
    if (!n) return;
    await persist({ name: n, vars: {} });
    setSelected(n);
    setCreating(false);
    setNewName("");
  };

  return (
    <div className="glass-card flex-1 flex min-h-0 overflow-hidden">
      {/* Env list */}
      <div className="w-52 flex-shrink-0 border-r border-border/50 flex flex-col">
        <div className="px-3 py-2.5 flex items-center justify-between border-b border-border/50">
          <span className="text-[10px] font-bold text-text-muted uppercase tracking-widest">Environments</span>
          <button onClick={() => setCreating(true)} className="text-text-muted hover:text-accent"><Plus size={14} /></button>
        </div>
        <div className="flex-1 overflow-y-auto p-2 flex flex-col gap-1">
          {environments.length === 0 && <p className="text-xs text-text-muted px-2 mt-2">No environments yet.</p>}
          {environments.map((e) => (
            <button
              key={e.name}
              onClick={() => setSelected(e.name)}
              className={`group flex items-center gap-2 px-2.5 py-2 rounded-lg text-left text-[13px] transition-all ${
                selected === e.name ? "bg-card-hover border border-accent/40" : "border border-transparent hover:bg-card-hover/60"
              }`}
            >
              <Layers3 size={13} className="text-accent flex-shrink-0" />
              <span className="truncate flex-1 text-text-primary">{e.name}</span>
              <span className="text-[10px] text-text-muted">{Object.keys(e.vars).length}</span>
              <Trash2
                size={12}
                onClick={(ev) => { ev.stopPropagation(); setPendingDelete(e.name); }}
                className="opacity-0 group-hover:opacity-100 text-text-muted hover:text-danger"
              />
            </button>
          ))}
        </div>
      </div>

      {/* Var editor */}
      <div className="flex-1 flex flex-col min-w-0">
        {!active ? (
          <Empty text="Select or create an environment." />
        ) : (
          <>
            <div className="px-4 py-2.5 flex items-center justify-between border-b border-border/50">
              <span className="text-sm font-semibold text-text-primary">{active.name}</span>
              <button onClick={saveRows} className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-accent text-bg text-xs font-bold">
                <Check size={13} /> Save
              </button>
            </div>
            <div className="flex-1 overflow-y-auto p-4 flex flex-col gap-2">
              <p className="text-[11px] text-text-muted mb-1">Reference these as <code>{"{{name}}"}</code> in URL, headers, or body.</p>
              {rows.map((r) => (
                <div key={r.id} className="flex gap-2">
                  <input
                    value={r.key}
                    onChange={(e) => setRows((rs) => rs.map((x) => x.id === r.id ? { ...x, key: e.target.value } : x))}
                    placeholder="VARIABLE"
                    className="input-base py-1.5 text-xs flex-1 font-mono"
                  />
                  <input
                    value={r.value}
                    onChange={(e) => setRows((rs) => rs.map((x) => x.id === r.id ? { ...x, value: e.target.value } : x))}
                    placeholder="value"
                    className="input-base py-1.5 text-xs flex-1"
                  />
                  <button
                    onClick={() => setRows((rs) => rs.filter((x) => x.id !== r.id))}
                    className="w-8 flex items-center justify-center rounded-lg text-text-muted hover:text-danger"
                  >
                    <Trash2 size={13} />
                  </button>
                </div>
              ))}
              <button
                onClick={() => setRows((rs) => [...rs, { id: crypto.randomUUID(), key: "", value: "" }])}
                className="btn-secondary self-start mt-1"
              >
                <Plus size={13} /> Add variable
              </button>
            </div>
          </>
        )}
      </div>

      {/* Create env modal */}
      <Modal
        open={creating}
        title="New environment"
        onClose={() => setCreating(false)}
        footer={
          <>
            <button onClick={() => setCreating(false)} className="btn-secondary px-3 py-1.5">Cancel</button>
            <button onClick={createEnv} className="px-3 py-1.5 rounded-lg bg-accent text-bg text-xs font-bold">Create</button>
          </>
        }
      >
        <input
          autoFocus value={newName}
          onChange={(e) => setNewName(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && createEnv()}
          placeholder="e.g. dev, prod…"
          className="input-base w-full py-2 text-sm"
        />
      </Modal>

      {/* Delete env modal */}
      <Modal
        open={!!pendingDelete}
        title="Delete environment?"
        onClose={() => setPendingDelete(null)}
        footer={
          <>
            <button onClick={() => setPendingDelete(null)} className="btn-secondary px-3 py-1.5">Cancel</button>
            <button
              onClick={async () => { if (pendingDelete) { await deleteEnvironment(pendingDelete); if (selected === pendingDelete) setSelected(null); } setPendingDelete(null); }}
              className="px-3 py-1.5 rounded-lg bg-danger text-white text-xs font-bold"
            >Delete</button>
          </>
        }
      >
        <p>Permanently delete environment <b className="text-text-primary">{pendingDelete}</b> and its variables.</p>
      </Modal>
    </div>
  );
}

function Empty({ text }: { text: string }) {
  return (
    <div className="flex-1 flex items-center justify-center text-text-muted text-sm">{text}</div>
  );
}
