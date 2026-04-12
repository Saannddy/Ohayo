import threading
import time
from datetime import datetime

import requests


class Scheduler:
    """HTTP request scheduler — runs requests on a repeating timer."""

    def __init__(self):
        self.is_running = False
        self._thread = None
        self._callbacks: dict = {}
        self.reset_stats()

    # ── Stats ──────────────────────────────────────────────────────────
    def reset_stats(self):
        self.request_count = 0
        self.success_count = 0
        self.total_ms = 0.0
        self.last_status = None

    @property
    def stats(self):
        total = self.request_count
        pct   = (self.success_count / total * 100) if total > 0 else 0.0
        avg   = (self.total_ms / total)             if total > 0 else 0.0
        return {
            "total":       total,
            "success":     self.success_count,
            "success_pct": pct,
            "avg_ms":      avg,
            "last_status": self.last_status,
        }

    # ── Event callbacks ─────────────────────────────────────────────────
    def on(self, event: str, callback):
        self._callbacks[event] = callback
        return self

    def _emit(self, event: str, *args, **kwargs):
        cb = self._callbacks.get(event)
        if cb:
            try:
                cb(*args, **kwargs)
            except Exception:
                pass

    # ── Control ──────────────────────────────────────────────────────────
    def start(self, url: str, method: str, headers: dict,
              body: str, interval: int, stop_time):
        if self.is_running:
            return
        self.reset_stats()
        self.is_running = True
        self._thread = threading.Thread(
            target=self._loop,
            args=(url, method, headers, body, interval, stop_time),
            daemon=True,
        )
        self._thread.start()

    def stop(self):
        self.is_running = False

    # ── Internal loop ────────────────────────────────────────────────────
    def _loop(self, url, method, headers, body, interval, stop_time):
        try:
            while self.is_running:
                if datetime.now().time() >= stop_time:
                    self._emit("completed", stop_time)
                    break

                self._make_request(url, method, headers, body)

                if not self.is_running:
                    break

                # tick-by-tick countdown
                for remaining in range(interval, 0, -1):
                    if not self.is_running:
                        break
                    self._emit("countdown", remaining, interval)
                    time.sleep(1)

        except Exception as e:
            self._emit("error_event", str(e))
        finally:
            self.is_running = False
            self._emit("finished")

    def _make_request(self, url, method, headers, body):
        t0 = time.time()
        ts = datetime.now().strftime("%H:%M:%S")
        try:
            resp = requests.request(
                method=method,
                url=url,
                headers=headers or {},
                data=body if body else None,
                timeout=10,
            )
            elapsed = (time.time() - t0) * 1000
            self.request_count += 1
            self.total_ms += elapsed
            code = resp.status_code
            if 200 <= code < 300:
                self.success_count += 1
            self.last_status = code
            self._emit("response", {
                "timestamp":  ts,
                "count":      self.request_count,
                "method":     method,
                "status":     code,
                "elapsed_ms": elapsed,
                "url":        url,
            })

        except requests.exceptions.Timeout:
            elapsed = (time.time() - t0) * 1000
            self.request_count += 1
            self.total_ms += elapsed
            self._emit("req_error", {"timestamp": ts, "count": self.request_count,
                                     "error": "Timed out (10 s)", "elapsed_ms": elapsed})

        except requests.exceptions.RequestException as e:
            elapsed = (time.time() - t0) * 1000
            self.request_count += 1
            self.total_ms += elapsed
            self._emit("req_error", {"timestamp": ts, "count": self.request_count,
                                     "error": str(e), "elapsed_ms": elapsed})
