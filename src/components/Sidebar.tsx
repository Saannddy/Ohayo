import { useEffect, useState } from "react";
import { FolderOpen, Download, Upload, FolderPlus, FilePlus, Sun, Moon } from "lucide-react";
import { useCollections } from "../hooks/useCollections";
import { useTheme } from "../hooks/useTheme";
import { useAppStore } from "../store/appStore";
import { CollectionTree } from "./CollectionTree";
import { Modal } from "./Modal";
import type { TreeNode } from "../types";

export function Sidebar() {
  const {
    restoreLast, pickAndOpenCollection, importCollection, exportCollection,
    loadRequest, createRequest, renameEntry, deleteEntry, createFolder, moveEntry,
  } = useCollections();
  const { isDark, toggleTheme } = useTheme();
  const { tree, collectionRoot } = useAppStore();
  const [rootDragOver, setRootDragOver] = useState(false);

  const [pendingDelete, setPendingDelete] = useState<TreeNode | null>(null);
  const [creatingFolder, setCreatingFolder] = useState(false);
  const [folderName, setFolderName] = useState("");

  useEffect(() => { restoreLast(); }, [restoreLast]);

  const confirmDelete = async () => {
    if (pendingDelete) await deleteEntry(pendingDelete.path);
    setPendingDelete(null);
  };

  const confirmFolder = async () => {
    const n = folderName.trim();
    if (n && collectionRoot) await createFolder(collectionRoot, n);
    setCreatingFolder(false);
    setFolderName("");
  };

  return (
    <aside className="w-64 flex-shrink-0 flex flex-col bg-sidebar border-r border-border/50 overflow-hidden">
      {/* Brand */}
      <div className="px-5 pt-5 pb-4 flex-shrink-0">
        <div className="text-2xl font-bold text-gradient-acc tracking-tight">おはよう</div>
        <div className="text-[10px] text-text-muted mt-0.5 tracking-widest uppercase">API Waker · v2</div>
      </div>

      <div className="h-px bg-border/50 mx-4 flex-shrink-0" />

      {/* Collection toolbar */}
      <div className="px-3 pt-3 pb-2 flex-shrink-0 flex flex-col gap-2">
        {collectionRoot ? (
          <button onClick={createRequest} className="btn-secondary w-full justify-center">
            <FilePlus size={13} />
            New Request
          </button>
        ) : (
          <button onClick={pickAndOpenCollection} className="btn-secondary w-full justify-center">
            <FolderOpen size={13} />
            Open collection
          </button>
        )}
        <div className="flex gap-1.5">
          <IconBtn title="New folder" onClick={() => collectionRoot && setCreatingFolder(true)} disabled={!collectionRoot}><FolderPlus size={13} /></IconBtn>
          <IconBtn title="Switch collection" onClick={pickAndOpenCollection}><FolderOpen size={13} /></IconBtn>
          <IconBtn title="Import collection" onClick={importCollection}><Upload size={13} /></IconBtn>
          <IconBtn title="Export collection" onClick={exportCollection} disabled={!collectionRoot}><Download size={13} /></IconBtn>
        </div>
      </div>

      {/* Tree */}
      <div
        className={`flex-1 overflow-y-auto px-2 pb-2 min-h-0 rounded-lg ${rootDragOver ? "bg-accent/10 ring-1 ring-accent/40" : ""}`}
        onDragOver={(e) => { if (collectionRoot) { e.preventDefault(); setRootDragOver(true); } }}
        onDragLeave={() => setRootDragOver(false)}
        onDrop={(e) => {
          e.preventDefault();
          setRootDragOver(false);
          const s = useAppStore.getState();
          const from = s.draggingPath || e.dataTransfer.getData("text/plain");
          s.setDraggingPath(null);
          if (from && collectionRoot) moveEntry(from, collectionRoot);
        }}
      >
        {creatingFolder && (
          <div className="flex gap-1.5 px-1 py-1.5">
            <input
              autoFocus value={folderName}
              onChange={(e) => setFolderName(e.target.value)}
              onKeyDown={(e) => { if (e.key === "Enter") confirmFolder(); if (e.key === "Escape") setCreatingFolder(false); }}
              placeholder="Folder name…"
              className="input-base py-1 text-xs flex-1"
            />
            <button onClick={confirmFolder} className="px-2 rounded-md bg-accent text-bg text-xs font-bold">✓</button>
          </div>
        )}
        {!tree ? (
          <div className="text-center text-text-muted text-xs mt-6 leading-relaxed px-3">
            No collection open.{"\n"}Open a folder to store requests as <code>.ohy</code> files.
          </div>
        ) : tree.children.length === 0 ? (
          <div className="text-center text-text-muted text-xs mt-6 leading-relaxed px-3">
            Empty collection.{"\n"}Save a request to get started.
          </div>
        ) : (
          <CollectionTree
            node={tree}
            onOpenRequest={(n) => loadRequest(n.path)}
            onDelete={setPendingDelete}
            onMove={moveEntry}
            onRename={(path, name) => renameEntry(path, name)}
          />
        )}
      </div>

      <div className="h-px bg-border/50 mx-4 flex-shrink-0" />

      {/* Theme toggle */}
      <div className="px-4 py-4 flex items-center justify-between flex-shrink-0">
        <span className="text-xs text-text-muted">{isDark ? "Dark mode" : "Light mode"}</span>
        <button
          onClick={toggleTheme}
          className="w-8 h-8 flex items-center justify-center rounded-lg text-text-muted hover:text-accent hover:bg-surface transition-all"
        >
          {isDark ? <Sun size={15} /> : <Moon size={15} />}
        </button>
      </div>

      {/* Delete confirmation */}
      <Modal
        open={!!pendingDelete}
        title={pendingDelete?.isDir ? "Delete folder?" : "Delete request?"}
        onClose={() => setPendingDelete(null)}
        footer={
          <>
            <button onClick={() => setPendingDelete(null)} className="btn-secondary px-3 py-1.5">Cancel</button>
            <button onClick={confirmDelete} className="px-3 py-1.5 rounded-lg bg-danger text-white text-xs font-bold">Delete</button>
          </>
        }
      >
        {pendingDelete && (
          <div className="flex flex-col gap-2">
            <p>
              {pendingDelete.isDir
                ? <>This permanently deletes the folder <b className="text-text-primary">{pendingDelete.name}</b> and everything inside it.</>
                : <>This permanently deletes the request <b className="text-text-primary">{pendingDelete.name}</b>{pendingDelete.method ? <> (<span className="font-mono">{pendingDelete.method}</span>)</> : null}.</>}
            </p>
            <code className="text-[10px] text-text-muted break-all bg-input-bg/60 rounded px-2 py-1.5">{pendingDelete.path}</code>
          </div>
        )}
      </Modal>
    </aside>
  );
}

function IconBtn({ children, title, onClick, disabled }: { children: React.ReactNode; title: string; onClick: () => void; disabled?: boolean }) {
  return (
    <button
      title={title} onClick={onClick} disabled={disabled}
      className="flex-1 h-8 flex items-center justify-center rounded-lg bg-surface border border-border
                 text-text-muted hover:text-accent hover:border-accent/40 transition-all
                 disabled:opacity-40 disabled:cursor-not-allowed"
    >
      {children}
    </button>
  );
}
