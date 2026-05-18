use std::sync::{Arc, atomic::{AtomicBool, Ordering}};
use tokio::time::{sleep, Duration};
use chrono::{Local, NaiveTime};
use tauri::{AppHandle, Emitter};
use crate::http_client::{make_request, RequestResult};
use crate::types::{ScheduleConfig, CountdownPayload, SentPayload, StatsPayload};

pub struct SchedulerHandle {
    stop_flag: Option<Arc<AtomicBool>>,
}

impl Default for SchedulerHandle {
    fn default() -> Self {
        Self { stop_flag: None }
    }
}

impl SchedulerHandle {
    pub fn is_running(&self) -> bool {
        self.stop_flag.as_ref().map_or(false, |f| f.load(Ordering::SeqCst))
    }

    pub fn start(&mut self, config: ScheduleConfig, client: reqwest::Client, app: AppHandle) -> Result<(), String> {
        if self.is_running() {
            return Err("Scheduler already running".into());
        }
        let flag = Arc::new(AtomicBool::new(true));
        self.stop_flag = Some(flag.clone());
        tokio::spawn(async move { run_scheduler(config, client, app, flag).await; });
        Ok(())
    }

    pub fn stop(&mut self) {
        if let Some(f) = &self.stop_flag { f.store(false, Ordering::SeqCst); }
    }
}

async fn run_scheduler(cfg: ScheduleConfig, client: reqwest::Client, app: AppHandle, running: Arc<AtomicBool>) {
    let mut total = 0u32;
    let mut success = 0u32;
    let mut total_ms = 0.0f64;
    let mut last_status: Option<u16> = None;

    let emit_stats = |t: u32, s: u32, ms: f64, ls: Option<u16>| {
        let _ = app.emit("scheduler:stats", StatsPayload {
            total: t, success: s,
            success_pct: if t > 0 { s as f64 / t as f64 * 100.0 } else { 0.0 },
            avg_ms: if t > 0 { ms / t as f64 } else { 0.0 },
            last_status: ls,
        });
    };

    if cfg.mode == "single" {
        total += 1;
        let res = make_request(&client, &cfg.url, &cfg.method, &cfg.headers, &cfg.body, total).await;
        handle_result(res, &mut success, &mut total_ms, &mut last_status, &app);
        emit_stats(total, success, total_ms, last_status);
        let _ = app.emit("scheduler:completed_single", ());
        running.store(false, Ordering::SeqCst);
        let _ = app.emit("scheduler:finished", ());
        return;
    }

    // Wait until start_time if set (continuous mode only)
    if cfg.mode == "continuous" && !cfg.start_time.is_empty() {
        if let Ok(st) = NaiveTime::parse_from_str(&cfg.start_time, "%H:%M") {
            while running.load(Ordering::SeqCst) {
                if Local::now().time() >= st { break; }
                let _ = app.emit("scheduler:waiting", cfg.start_time.clone());
                sleep(Duration::from_secs(1)).await;
            }
        }
    }

    let stop_time = if cfg.mode == "continuous" && !cfg.stop_time.is_empty() {
        NaiveTime::parse_from_str(&cfg.stop_time, "%H:%M").ok()
    } else { None };
    let mut sent_count = 0u32;

    while running.load(Ordering::SeqCst) {
        if cfg.mode == "continuous" {
            if let Some(st) = stop_time {
                if Local::now().time() >= st {
                    let _ = app.emit("scheduler:completed", cfg.stop_time.clone());
                    break;
                }
            }
        }
        if cfg.mode == "count" && sent_count >= cfg.count {
            let _ = app.emit("scheduler:completed_count", sent_count);
            break;
        }

        total += 1;
        let res = make_request(&client, &cfg.url, &cfg.method, &cfg.headers, &cfg.body, total).await;
        handle_result(res, &mut success, &mut total_ms, &mut last_status, &app);
        emit_stats(total, success, total_ms, last_status);
        sent_count += 1;
        let target = if cfg.mode == "count" { Some(cfg.count) } else { None };
        let _ = app.emit("scheduler:sent", SentPayload { count: sent_count, target });

        if cfg.mode == "count" && sent_count >= cfg.count {
            let _ = app.emit("scheduler:completed_count", sent_count);
            break;
        }
        if !running.load(Ordering::SeqCst) { break; }

        for rem in (1..=cfg.interval).rev() {
            if !running.load(Ordering::SeqCst) { break; }
            let _ = app.emit("scheduler:countdown", CountdownPayload { remaining: rem, total: cfg.interval });
            sleep(Duration::from_secs(1)).await;
        }
    }

    running.store(false, Ordering::SeqCst);
    let _ = app.emit("scheduler:finished", ());
}

fn handle_result(res: RequestResult, success: &mut u32, total_ms: &mut f64, last_status: &mut Option<u16>, app: &AppHandle) {
    match res {
        RequestResult::Success(d) => {
            if d.status >= 200 && d.status < 300 { *success += 1; }
            *total_ms += d.elapsed_ms;
            *last_status = Some(d.status);
            let _ = app.emit("scheduler:response", &d);
        }
        RequestResult::Failure(d) => {
            *total_ms += d.elapsed_ms;
            let _ = app.emit("scheduler:req_error", &d);
        }
    }
}
