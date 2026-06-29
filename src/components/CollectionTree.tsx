import { useState } from "react";
import { ChevronRight, FolderClosed, FolderOpen, Trash2 } from "lucide-react";
import type { TreeNode } from "../types";
import { useAppStore } from "../store/appStore";
import { METHOD_COLORS } from "../theme/tokens";

interface Props {
  node: TreeNode;
  depth?: number;
  onOpenRequest: (node: TreeNode) => void;
  onDelete: (node: TreeNode) => void;
  onMove: (fromPath: string, destDir: string) => void;
  onRename: (path: string, newName: string) => void;
}

export function CollectionTree({ node, depth = 0, ...rest }: Props) {
  // The root node renders only its children (no header row).
  if (depth === 0) {
    return (
      <div className="flex flex-col gap-0.5">
        {node.children.map((child) => (
          <TreeRow key={child.path} node={child} depth={1} {...rest} />
        ))}
      </div>
    );
  }
  return <TreeRow node={node} depth={depth} {...rest} />;
}

type RowProps = Required<Pick<Props, "node" | "depth">> & Omit<Props, "node" | "depth">;

function TreeRow({ node, depth, onOpenRequest, onDelete, onMove, onRename }: RowProps) {
  const [open, setOpen] = useState(true);
  const [dragOver, setDragOver] = useState(false);
  const [editing, setEditing] = useState(false);
  const [draft, setDraft] = useState(node.name);
  const activePath = useAppStore((s) => s.activeRequestPath);
  const pad = { paddingLeft: `${depth * 12}px` };

  const startDrag = (e: React.DragEvent) => {
    e.stopPropagation();
    // WebKit drops custom MIME types, so the path also rides in the store.
    useAppStore.getState().setDraggingPath(node.path);
    e.dataTransfer.setData("text/plain", node.path);
    e.dataTransfer.effectAllowed = "move";
  };
  const endDrag = () => useAppStore.getState().setDraggingPath(null);

  const beginEdit = (e: React.MouseEvent) => {
    e.stopPropagation();
    setDraft(node.name);
    setEditing(true);
  };
  const commitEdit = () => {
    const n = draft.trim();
    if (n && n !== node.name) onRename(node.path, n);
    setEditing(false);
  };

  const NameEditor = (
    <input
      autoFocus
      value={draft}
      onChange={(e) => setDraft(e.target.value)}
      onClick={(e) => e.stopPropagation()}
      onKeyDown={(e) => {
        e.stopPropagation();
        if (e.key === "Enter") commitEdit();
        if (e.key === "Escape") setEditing(false);
      }}
      onBlur={commitEdit}
      className="input-base py-0.5 text-[13px] flex-1 min-w-0"
    />
  );

  if (node.isDir) {
    const onDrop = (e: React.DragEvent) => {
      e.preventDefault();
      e.stopPropagation();
      setDragOver(false);
      const from = useAppStore.getState().draggingPath || e.dataTransfer.getData("text/plain");
      useAppStore.getState().setDraggingPath(null);
      if (from && from !== node.path) onMove(from, node.path);
    };
    return (
      <div>
        <div
          draggable={!editing}
          onDragStart={startDrag}
          onDragEnd={endDrag}
          onDragOver={(e) => { e.preventDefault(); e.stopPropagation(); setDragOver(true); }}
          onDragLeave={() => setDragOver(false)}
          onDrop={onDrop}
          className={`group flex items-center gap-1.5 px-2 py-1.5 rounded-lg cursor-pointer select-none border ${
            dragOver ? "bg-accent/15 border-accent/50" : "border-transparent hover:bg-card-hover/60"
          }`}
          style={pad}
          onClick={() => !editing && setOpen((o) => !o)}
          onDoubleClick={beginEdit}
        >
          <ChevronRight size={12} className={`text-text-muted transition-transform ${open ? "rotate-90" : ""}`} />
          {open ? <FolderOpen size={13} className="text-accent" /> : <FolderClosed size={13} className="text-text-muted" />}
          {editing ? NameEditor : (
            <span className="text-[13px] font-medium text-text-secondary truncate flex-1">{node.name}</span>
          )}
          {!editing && <DeleteBtn onClick={(e) => { e.stopPropagation(); onDelete(node); }} />}
        </div>
        {open && node.children.map((c) => (
          <TreeRow key={c.path} node={c} depth={depth + 1} onOpenRequest={onOpenRequest} onDelete={onDelete} onMove={onMove} onRename={onRename} />
        ))}
      </div>
    );
  }

  const active = node.path === activePath;
  const method = (node.method || "GET").toUpperCase();
  return (
    <div
      draggable={!editing}
      onDragStart={startDrag}
      onDragEnd={endDrag}
      className={`group flex items-center gap-2 px-2 py-1.5 rounded-lg cursor-pointer select-none border ${
        active ? "bg-card-hover border-accent/40" : "border-transparent hover:bg-card-hover/60"
      }`}
      style={pad}
      onClick={() => !editing && onOpenRequest(node)}
      onDoubleClick={beginEdit}
    >
      <span className={`text-[9px] font-bold w-9 text-right ${METHOD_COLORS[method] ?? "text-text-muted"}`}>{method}</span>
      {editing ? NameEditor : (
        <span className="text-[13px] text-text-primary truncate flex-1">{node.name}</span>
      )}
      {!editing && <DeleteBtn onClick={(e) => { e.stopPropagation(); onDelete(node); }} />}
    </div>
  );
}

function DeleteBtn({ onClick }: { onClick: (e: React.MouseEvent) => void }) {
  return (
    <button
      onClick={onClick}
      className="opacity-0 group-hover:opacity-100 w-5 h-5 flex items-center justify-center rounded text-text-muted hover:text-danger hover:bg-danger/10 transition-all"
    >
      <Trash2 size={11} />
    </button>
  );
}
