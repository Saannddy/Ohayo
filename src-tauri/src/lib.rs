use tauri::AppHandle;

pub mod types;
pub mod http_client;
pub mod collections;
pub mod config;
pub mod scheduler;

use types::*;
use scheduler::SchedulerHandle;

pub struct AppState {
    pub scheduler: tokio::sync::Mutex<SchedulerHandle>,
    pub client: reqwest::Client,
}

// ── Scheduler ───────────────────────────────────────────────────────────

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
async fn is_scheduler_running(state: tauri::State<'_, AppState>) -> Result<bool, String> {
    Ok(state.scheduler.lock().await.is_running())
}

// ── Collections ─────────────────────────────────────────────────────────

#[tauri::command]
fn init_collection(root: String, name: String) -> Result<(), String> {
    collections::init_collection(&root, &name)
}

#[tauri::command]
fn read_collection_tree(root: String) -> Result<TreeNode, String> {
    collections::read_tree(&root)
}

#[tauri::command]
fn read_request(path: String) -> Result<RequestFile, String> {
    collections::read_request(&path)
}

#[tauri::command]
fn save_request(dir: String, request: RequestFile) -> Result<String, String> {
    collections::save_request(&dir, request)
}

#[tauri::command]
fn write_request(path: String, request: RequestFile) -> Result<(), String> {
    collections::write_request(&path, request)
}

#[tauri::command]
fn delete_entry(path: String) -> Result<(), String> {
    collections::delete_entry(&path)
}

#[tauri::command]
fn create_folder(parent: String, name: String) -> Result<String, String> {
    collections::create_folder(&parent, &name)
}

#[tauri::command]
fn move_entry(from: String, dest_dir: String) -> Result<String, String> {
    collections::move_entry(&from, &dest_dir)
}

#[tauri::command]
fn new_blank_request(dir: String) -> Result<String, String> {
    collections::new_blank_request(&dir)
}

#[tauri::command]
fn rename_entry(path: String, new_name: String) -> Result<String, String> {
    collections::rename_entry(&path, &new_name)
}

// ── Environments ────────────────────────────────────────────────────────

#[tauri::command]
fn list_environments(root: String) -> Vec<Environment> {
    collections::list_environments(&root)
}

#[tauri::command]
fn save_environment(root: String, environment: Environment) -> Result<(), String> {
    collections::save_environment(&root, environment)
}

#[tauri::command]
fn delete_environment(root: String, name: String) -> Result<(), String> {
    collections::delete_environment(&root, &name)
}

// ── Import / Export ─────────────────────────────────────────────────────

#[tauri::command]
fn export_collection(root: String, dest: String) -> Result<(), String> {
    collections::export_collection(&root, &dest)
}

#[tauri::command]
fn import_collection(file: String, dest_parent: String) -> Result<String, String> {
    collections::import_collection(&file, &dest_parent)
}

// ── App config (last opened collection) ─────────────────────────────────

#[tauri::command]
fn get_last_collection() -> Option<String> {
    config::load().last_collection
}

#[tauri::command]
fn set_last_collection(path: Option<String>) -> Result<(), String> {
    config::set_last_collection(path)
}

pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_dialog::init())
        .manage(AppState {
            scheduler: tokio::sync::Mutex::new(SchedulerHandle::default()),
            client: reqwest::Client::new(),
        })
        .invoke_handler(tauri::generate_handler![
            start_scheduler,
            stop_scheduler,
            is_scheduler_running,
            init_collection,
            read_collection_tree,
            read_request,
            save_request,
            write_request,
            delete_entry,
            create_folder,
            move_entry,
            new_blank_request,
            rename_entry,
            list_environments,
            save_environment,
            delete_environment,
            export_collection,
            import_collection,
            get_last_collection,
            set_last_collection,
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
