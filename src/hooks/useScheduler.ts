import { useCallback } from "react";
import { invoke } from "@tauri-apps/api/core";
import { listen, type UnlistenFn } from "@tauri-apps/api/event";
import { useAppStore } from "../store/appStore";
import type { ResponsePayload, ErrorPayload, CountdownPayload, StatsPayload, LogEntry } from "../types";
import { getLogTag } from "../types";

export function useScheduler() {
  const store = useAppStore();

  const setupListeners = useCallback((): (() => void) => {
    const tasks: Promise<UnlistenFn>[] = [];

    tasks.push(listen<ResponsePayload>("scheduler:response", ({ payload: p }) => {
      const entry: LogEntry = {
        id: `${Date.now()}-${Math.random()}`,
        timestamp: p.timestamp, count: p.count, method: p.method,
        status: p.status, elapsedMs: p.elapsedMs, tag: getLogTag(p.status),
      };
      store.addLogEntry(entry);
    }));

    tasks.push(listen<ErrorPayload>("scheduler:req_error", ({ payload: p }) => {
      const entry: LogEntry = {
        id: `${Date.now()}-${Math.random()}`,
        timestamp: p.timestamp, count: p.count, method: "ERROR",
        error: p.error, elapsedMs: p.elapsedMs, tag: "error",
      };
      store.addLogEntry(entry);
    }));

    tasks.push(listen<StatsPayload>("scheduler:stats", ({ payload: p }) => {
      store.setStats({
        total: p.total, success: p.success,
        successPct: p.successPct, avgMs: p.avgMs, lastStatus: p.lastStatus,
      });
    }));

    tasks.push(listen<CountdownPayload>("scheduler:countdown", ({ payload: p }) => {
      store.setProgress(p.remaining / p.total);
      store.setStatus(`Next request in ${p.remaining}s…`, "muted");
    }));

    tasks.push(listen<{ count: number; target: number | null }>("scheduler:sent", ({ payload: p }) => {
      if (p.target != null) {
        store.setStatus(`Sent ${p.count} of ${p.target}…`, "success");
      }
    }));

    tasks.push(listen<string>("scheduler:completed", ({ payload }) => {
      store.setStatus(`Completed at ${payload}`, "success");
      store.setProgress(0);
    }));

    tasks.push(listen<number>("scheduler:completed_count", ({ payload }) => {
      store.setStatus(`Completed — ${payload} requests sent`, "success");
      store.setProgress(1);
    }));

    tasks.push(listen("scheduler:completed_single", () => {
      store.setStatus("Request sent.", "success");
      store.setProgress(1);
    }));

    tasks.push(listen<string>("scheduler:waiting", ({ payload }) => {
      store.setStatus(`Waiting to start at ${payload}…`, "muted");
      store.setProgress(1);
    }));

    tasks.push(listen("scheduler:finished", () => {
      store.setRunning(false);
      if (store.statusMessage === "Running…") {
        store.setStatus("Stopped", "danger");
      }
      store.setProgress(0);
    }));

    return () => { Promise.all(tasks).then((fns) => fns.forEach((fn) => fn())); };
  }, []);

  const startScheduler = useCallback(async () => {
    const s = useAppStore.getState();
    await invoke("start_scheduler", {
      config: {
        url: s.url, method: s.method, headers: s.getHeadersMap(),
        body: s.mode !== "single" ? s.body : "",
        mode: s.mode,
        interval: parseInt(s.interval) || 5,
        count: parseInt(s.count) || 1,
        startTime: s.startTime,
        stopTime: s.stopTime,
      },
    });
    store.setRunning(true);
    store.setStatus("Running…", "success");
    store.setProgress(1);
  }, []);

  const stopScheduler = useCallback(async () => {
    await invoke("stop_scheduler");
    store.setRunning(false);
    store.setStatus("Stopped", "danger");
    store.setProgress(0);
  }, []);

  return { setupListeners, startScheduler, stopScheduler };
}
