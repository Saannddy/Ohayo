use std::collections::HashMap;
use std::path::PathBuf;
use crate::types::Profile;

fn profiles_path() -> PathBuf {
    dirs::home_dir()
        .unwrap_or_else(|| PathBuf::from("."))
        .join(".ohayo_profiles.json")
}

fn load_all() -> HashMap<String, Profile> {
    std::fs::read_to_string(profiles_path())
        .ok()
        .and_then(|s| serde_json::from_str(&s).ok())
        .unwrap_or_default()
}

fn save_all(profiles: &HashMap<String, Profile>) -> Result<(), String> {
    let json = serde_json::to_string_pretty(profiles).map_err(|e| e.to_string())?;
    std::fs::write(profiles_path(), json).map_err(|e| e.to_string())
}

pub fn get_profiles() -> Vec<(String, Profile)> {
    let mut entries: Vec<_> = load_all().into_iter().collect();
    entries.sort_by_key(|(name, _)| name.clone());
    entries
}

pub fn save_profile(name: String, profile: Profile) -> Result<(), String> {
    let mut all = load_all();
    all.insert(name, profile);
    save_all(&all)
}

pub fn delete_profile(name: &str) -> Result<(), String> {
    let mut all = load_all();
    all.remove(name);
    save_all(&all)
}

pub fn load_profile(name: &str) -> Option<Profile> {
    load_all().remove(name)
}
