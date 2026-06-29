import { create } from "zustand";
import type { Environment, HttpMethod, LogEntry, LogFilter, Page, ScheduleMode, Stats, TreeNode } from "../types";

interface HeaderRow { id: string; key: string; value: string; }

interface AppStore {
  url: string;
  method: HttpMethod;
  mode: ScheduleMode;
  interval: string;
  count: string;
  startTime: string;
  stopTime: string;
  headers: HeaderRow[];
  body: string;
  isRunning: boolean;
  statusMessage: string;
  statusColor: "muted" | "success" | "danger";
  progress: number;
  logEntries: LogEntry[];
  logFilter: LogFilter;
  stats: Stats;
  isDark: boolean;

  // Navigation
  page: Page;
  selectedLogId: string | null;

  // Collections
  collectionRoot: string | null;
  tree: TreeNode | null;
  activeRequestPath: string | null;

  // Environments
  environments: Environment[];
  activeEnvName: string | null;

  setUrl: (v: string) => void;
  setMethod: (v: HttpMethod) => void;
  setMode: (v: ScheduleMode) => void;
  setInterval: (v: string) => void;
  setCount: (v: string) => void;
  setStartTime: (v: string) => void;
  setStopTime: (v: string) => void;
  setBody: (v: string) => void;
  setRunning: (v: boolean) => void;
  setStatus: (msg: string, color: "muted" | "success" | "danger") => void;
  setProgress: (v: number) => void;
  addHeader: () => void;
  updateHeader: (id: string, field: "key" | "value", val: string) => void;
  removeHeader: (id: string) => void;
  setHeaders: (h: HeaderRow[]) => void;
  addLogEntry: (entry: LogEntry) => void;
  setLogFilter: (f: LogFilter) => void;
  setStats: (s: Stats) => void;
  clearLog: () => void;
  toggleTheme: () => void;

  setPage: (p: Page) => void;
  setSelectedLogId: (id: string | null) => void;

  setCollectionRoot: (path: string | null) => void;
  setTree: (t: TreeNode | null) => void;
  setActiveRequestPath: (p: string | null) => void;
  draggingPath: string | null;
  setDraggingPath: (p: string | null) => void;
  newRequest: () => void;

  setEnvironments: (envs: Environment[]) => void;
  setActiveEnvName: (name: string | null) => void;
  activeVars: () => Record<string, string>;

  applyRequest: (data: {
    url: string; method: string; mode: string;
    interval: string; count: string; startTime?: string; stopTime: string;
    headers: Record<string, string>; body: string;
  }) => void;
  getHeadersMap: () => Record<string, string>;
}

export const useAppStore = create<AppStore>((set, get) => ({
  url: "",
  method: "GET",
  mode: "continuous",
  interval: "5",
  count: "10",
  startTime: "",
  stopTime: "23:59",
  headers: [],
  body: "",
  isRunning: false,
  statusMessage: "Ready",
  statusColor: "muted",
  progress: 0,
  logEntries: [],
  logFilter: "ALL",
  stats: { total: 0, success: 0, successPct: 0, avgMs: 0, lastStatus: null },
  isDark: true,

  page: "request",
  selectedLogId: null,

  collectionRoot: null,
  tree: null,
  activeRequestPath: null,
  draggingPath: null,

  environments: [],
  activeEnvName: null,

  setUrl: (v) => set({ url: v }),
  setMethod: (v) => set({ method: v }),
  setMode: (v) => set({ mode: v }),
  setInterval: (v) => set({ interval: v }),
  setCount: (v) => set({ count: v }),
  setStartTime: (v) => set({ startTime: v }),
  setStopTime: (v) => set({ stopTime: v }),
  setBody: (v) => set({ body: v }),
  setRunning: (v) => set({ isRunning: v }),
  setStatus: (msg, color) => set({ statusMessage: msg, statusColor: color }),
  setProgress: (v) => set({ progress: v }),

  addHeader: () => set((s) => ({
    headers: [...s.headers, { id: crypto.randomUUID(), key: "", value: "" }],
  })),
  updateHeader: (id, field, val) => set((s) => ({
    headers: s.headers.map((h) => h.id === id ? { ...h, [field]: val } : h),
  })),
  removeHeader: (id) => set((s) => ({
    headers: s.headers.filter((h) => h.id !== id),
  })),
  setHeaders: (h) => set({ headers: h }),

  addLogEntry: (entry) => set((s) => ({
    logEntries: [...s.logEntries, entry].slice(-1000),
  })),
  setLogFilter: (f) => set({ logFilter: f }),
  setStats: (s) => set({ stats: s }),
  clearLog: () => set({ logEntries: [], stats: { total: 0, success: 0, successPct: 0, avgMs: 0, lastStatus: null } }),

  toggleTheme: () => set((s) => ({ isDark: !s.isDark })),

  setPage: (p) => set({ page: p }),
  setSelectedLogId: (id) => set({ selectedLogId: id }),

  setCollectionRoot: (path) => set({ collectionRoot: path }),
  setTree: (t) => set({ tree: t }),
  setActiveRequestPath: (p) => set({ activeRequestPath: p }),
  setDraggingPath: (p) => set({ draggingPath: p }),
  newRequest: () => set({
    url: "", method: "GET", mode: "continuous",
    interval: "5", count: "10", startTime: "", stopTime: "23:59",
    headers: [], body: "",
    activeRequestPath: null, page: "request",
    statusMessage: "Ready", statusColor: "muted",
  }),

  setEnvironments: (envs) => set((s) => ({
    environments: envs,
    activeEnvName: envs.some((e) => e.name === s.activeEnvName)
      ? s.activeEnvName
      : null,
  })),
  setActiveEnvName: (name) => set({ activeEnvName: name }),
  activeVars: () => {
    const { environments, activeEnvName } = get();
    return environments.find((e) => e.name === activeEnvName)?.vars ?? {};
  },

  applyRequest: (data) => set({
    url: data.url,
    method: data.method as HttpMethod,
    mode: data.mode as ScheduleMode,
    interval: data.interval,
    count: data.count,
    startTime: data.startTime ?? "",
    stopTime: data.stopTime,
    body: data.body,
    headers: Object.entries(data.headers).map(([key, value]) => ({
      id: crypto.randomUUID(), key, value,
    })),
  }),

  getHeadersMap: () => {
    const result: Record<string, string> = {};
    get().headers.forEach(({ key, value }) => { if (key.trim()) result[key.trim()] = value; });
    return result;
  },
}));
