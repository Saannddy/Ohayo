use tauri::AppHandle;

pub mod types;
pub mod http_client;
pub mod profiles;
pub mod scheduler;

use types::*;
use scheduler::SchedulerHandle;

pub struct AppState {
    pub scheduler: tokio::sync::Mutex<SchedulerHandle>,
    pub client: reqwest::Client,
}

#[tauri::command]
async fn start_scheduler(
    config: ScheduleConfig,
    state: tauri::State<'_, AppState>,
    app_handle: AppHandle,
) -> Result<(), String> {
    let mut handle = state.scheduler.lock().await;
    let client = state.client.clone();
    handle.start(config, client, app_handle)
}

#[tauri::command]
async fn stop_scheduler(state: tauri::State<'_, AppState>) -> Result<(), String> {
    state.scheduler.lock().await.stop();
    Ok(())
}

#[tauri::command]
fn get_profiles() -> Vec<(String, Profile)> {
    profiles::get_profiles()
}

#[tauri::command]
fn save_profile(name: String, profile: Profile) -> Result<(), String> {
    profiles::save_profile(name, profile)
}

#[tauri::command]
fn delete_profile(name: String) -> Result<(), String> {
    profiles::delete_profile(&name)
}

#[tauri::command]
fn load_profile(name: String) -> Option<Profile> {
    profiles::load_profile(&name)
}

#[tauri::command]
async fn is_scheduler_running(state: tauri::State<'_, AppState>) -> Result<bool, String> {
    Ok(state.scheduler.lock().await.is_running())
}

pub fn run() {
    tauri::Builder::default()
        .manage(AppState {
            scheduler: tokio::sync::Mutex::new(SchedulerHandle::default()),
            client: reqwest::Client::new(),
        })
        .invoke_handler(tauri::generate_handler![
            start_scheduler,
            stop_scheduler,
            get_profiles,
            save_profile,
            delete_profile,
            load_profile,
            is_scheduler_running,
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
