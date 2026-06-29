import { useCallback } from "react";
import { invoke } from "@tauri-apps/api/core";
import { open, save } from "@tauri-apps/plugin-dialog";
import { useAppStore } from "../store/appStore";
import type { Environment, RequestFile, TreeNode } from "../types";

export function useCollections() {
  const refreshTree = useCallback(async (root: string) => {
    const tree = await invoke<TreeNode>("read_collection_tree", { root });
    useAppStore.getState().setTree(tree);
    const envs = await invoke<Environment[]>("list_environments", { root });
    useAppStore.getState().setEnvironments(envs);
  }, []);

  const openCollection = useCallback(async (root: string) => {
    await refreshTree(root);
    useAppStore.getState().setCollectionRoot(root);
    await invoke("set_last_collection", { path: root });
  }, [refreshTree]);

  /** Prompt for a folder and open it as a collection (creating meta if absent). */
  const pickAndOpenCollection = useCallback(async () => {
    const dir = await open({ directory: true, multiple: false, title: "Open or create collection folder" });
    if (typeof dir !== "string") return;
    const name = dir.split(/[\\/]/).pop() || "Collection";
    // init is idempotent enough — only writes meta/env scaffold.
    await invoke("init_collection", { root: dir, name });
    await openCollection(dir);
  }, [openCollection]);

  /** Restore the last-opened collection on launch. */
  const restoreLast = useCallback(async () => {
    const last = await invoke<string | null>("get_last_collection");
    if (last) {
      try { await openCollection(last); } catch { /* folder gone — ignore */ }
    }
  }, [openCollection]);

  const loadRequest = useCallback(async (path: string) => {
    const req = await invoke<RequestFile>("read_request", { path });
    const s = useAppStore.getState();
    s.applyRequest({
      url: req.url, method: req.method, mode: req.mode,
      interval: req.interval, count: req.count,
      startTime: req.startTime ?? "", stopTime: req.stopTime,
      headers: req.headers, body: req.body,
    });
    s.setActiveRequestPath(path);
    s.setPage("request");
  }, []);

  /** Save the current editor state as a request. Defaults to the active request's
   *  folder (so re-saving stays put), else the collection root. */
  const saveRequest = useCallback(async (name: string, dir?: string) => {
    const s = useAppStore.getState();
    const root = s.collectionRoot;
    if (!root) return;
    const activeDir = s.activeRequestPath
      ? s.activeRequestPath.replace(/[\\/][^\\/]+$/, "")
      : null;
    dir = dir ?? activeDir ?? root;
    const req: RequestFile = {
      kind: "request",
      name,
      url: s.url, method: s.method, mode: s.mode,
      interval: s.interval, count: s.count,
      startTime: s.startTime, stopTime: s.stopTime,
      headers: s.getHeadersMap(), body: s.body,
    };
    const path = await invoke<string>("save_request", { dir, request: req });
    s.setActiveRequestPath(path);
    await refreshTree(root);
  }, [refreshTree]);

  /** Create a fresh untitled request (in the active folder, else root) and open it. */
  const createRequest = useCallback(async () => {
    const s = useAppStore.getState();
    const root = s.collectionRoot;
    if (!root) return;
    const activeDir = s.activeRequestPath
      ? s.activeRequestPath.replace(/[\\/][^\\/]+$/, "")
      : root;
    const path = await invoke<string>("new_blank_request", { dir: activeDir });
    await refreshTree(root);
    await loadRequest(path);
  }, [refreshTree, loadRequest]);

  /** Persist the current editor state into the active request file (in place). */
  const saveActive = useCallback(async (): Promise<boolean> => {
    const s = useAppStore.getState();
    const path = s.activeRequestPath;
    if (!path) return false;
    const name = (path.split(/[\\/]/).pop() || "").replace(/\.ohy$/, "");
    const req: RequestFile = {
      kind: "request", name,
      url: s.url, method: s.method, mode: s.mode,
      interval: s.interval, count: s.count,
      startTime: s.startTime, stopTime: s.stopTime,
      headers: s.getHeadersMap(), body: s.body,
    };
    await invoke("write_request", { path, request: req });
    if (s.collectionRoot) await refreshTree(s.collectionRoot);
    return true;
  }, [refreshTree]);

  const renameEntry = useCallback(async (path: string, newName: string): Promise<string> => {
    const s = useAppStore.getState();
    const newPath = await invoke<string>("rename_entry", { path, newName });
    if (s.activeRequestPath === path) s.setActiveRequestPath(newPath);
    if (s.collectionRoot) await refreshTree(s.collectionRoot);
    return newPath;
  }, [refreshTree]);

  const deleteEntry = useCallback(async (path: string) => {
    const root = useAppStore.getState().collectionRoot;
    await invoke("delete_entry", { path });
    if (root) await refreshTree(root);
  }, [refreshTree]);

  const createFolder = useCallback(async (parent: string, name: string) => {
    const root = useAppStore.getState().collectionRoot;
    await invoke("create_folder", { parent, name });
    if (root) await refreshTree(root);
  }, [refreshTree]);

  const moveEntry = useCallback(async (from: string, destDir: string) => {
    const s = useAppStore.getState();
    const root = s.collectionRoot;
    const newPath = await invoke<string>("move_entry", { from, destDir });
    if (s.activeRequestPath === from) s.setActiveRequestPath(newPath);
    if (root) await refreshTree(root);
  }, [refreshTree]);

  // ── Environments ──
  const saveEnvironment = useCallback(async (env: Environment) => {
    const root = useAppStore.getState().collectionRoot;
    if (!root) return;
    await invoke("save_environment", { root, environment: env });
    const envs = await invoke<Environment[]>("list_environments", { root });
    useAppStore.getState().setEnvironments(envs);
  }, []);

  const deleteEnvironment = useCallback(async (name: string) => {
    const root = useAppStore.getState().collectionRoot;
    if (!root) return;
    await invoke("delete_environment", { root, name });
    const envs = await invoke<Environment[]>("list_environments", { root });
    useAppStore.getState().setEnvironments(envs);
  }, []);

  // ── Import / Export ──
  const exportCollection = useCallback(async () => {
    const s = useAppStore.getState();
    const root = s.collectionRoot;
    if (!root) return;
    const name = s.tree?.name || "collection";
    const dest = await save({
      title: "Export collection",
      defaultPath: `${name}.ohy`,
      filters: [{ name: "Ohayo collection", extensions: ["ohy"] }],
    });
    if (typeof dest !== "string") return;
    await invoke("export_collection", { root, dest });
  }, []);

  const importCollection = useCallback(async () => {
    const file = await open({
      multiple: false,
      title: "Import collection",
      filters: [{ name: "Ohayo collection", extensions: ["ohy"] }],
    });
    if (typeof file !== "string") return;
    const destParent = await open({ directory: true, multiple: false, title: "Choose where to import" });
    if (typeof destParent !== "string") return;
    const newRoot = await invoke<string>("import_collection", { file, destParent });
    await openCollection(newRoot);
  }, [openCollection]);

  return {
    openCollection, pickAndOpenCollection, restoreLast, refreshTree,
    loadRequest, saveRequest, createRequest, saveActive, renameEntry,
    deleteEntry, createFolder, moveEntry,
    saveEnvironment, deleteEnvironment,
    exportCollection, importCollection,
  };
}
