export type HttpMethod = "GET" | "POST" | "PUT" | "PATCH" | "DELETE" | "HEAD" | "OPTIONS";
export type ScheduleMode = "single" | "count" | "continuous";
export type LogFilter = "ALL" | "2xx" | "3xx" | "4xx" | "5xx" | "ERR";
export type LogTag = "2xx" | "3xx" | "4xx" | "5xx" | "error";
export type Page = "request" | "logs" | "environments";

export interface ScheduleConfig {
  url: string;
  method: HttpMethod;
  headers: Record<string, string>;
  body: string;
  mode: ScheduleMode;
  interval: number;
  count: number;
  stopTime: string;
}

export interface LogEntry {
  id: string;
  timestamp: string;
  count: number;
  method: string;
  status?: number;
  elapsedMs: number;
  error?: string;
  tag: LogTag;
  url?: string;
  body?: string;
  headers?: Record<string, string>;
}

export interface Stats {
  total: number;
  success: number;
  successPct: number;
  avgMs: number;
  lastStatus: number | null;
}

/** A saved request, persisted as one `.ohy` file. */
export interface RequestFile {
  kind?: string;
  name: string;
  url: string;
  method: string;
  headers: Record<string, string>;
  body: string;
  mode: string;
  interval: string;
  count: string;
  startTime?: string;
  stopTime: string;
}

/** A node in the collection tree (folder or request). */
export interface TreeNode {
  name: string;
  path: string;
  isDir: boolean;
  method?: string | null;
  children: TreeNode[];
}

export interface Environment {
  name: string;
  vars: Record<string, string>;
}

export interface BundleNode {
  name: string;
  isDir: boolean;
  request?: RequestFile | null;
  children: BundleNode[];
}

export interface Bundle {
  name: string;
  root: BundleNode;
  environments: Environment[];
}

export interface ResponsePayload {
  timestamp: string;
  count: number;
  method: string;
  status: number;
  elapsedMs: number;
  url: string;
  body: string;
  headers: Record<string, string>;
}

export interface ErrorPayload {
  timestamp: string;
  count: number;
  error: string;
  elapsedMs: number;
}

export interface CountdownPayload {
  remaining: number;
  total: number;
}

export interface StatsPayload {
  total: number;
  success: number;
  successPct: number;
  avgMs: number;
  lastStatus: number | null;
}

export function getLogTag(status: number): LogTag {
  if (status < 300) return "2xx";
  if (status < 400) return "3xx";
  if (status < 500) return "4xx";
  return "5xx";
}
