use std::collections::HashMap;
use std::fs;
use std::path::{Path, PathBuf};
use crate::types::{RequestFile, TreeNode, Environment, Bundle, BundleNode};

pub const EXT: &str = "ohy";
const META_FILE: &str = "collection.ohy";
const ENV_DIR: &str = "environments";

fn is_request_file(p: &Path) -> bool {
    p.extension().and_then(|e| e.to_str()) == Some(EXT)
        && p.file_name().and_then(|n| n.to_str()) != Some(META_FILE)
}

fn file_stem(p: &Path) -> String {
    p.file_stem().and_then(|s| s.to_str()).unwrap_or("").to_string()
}

fn dir_name(p: &Path) -> String {
    p.file_name().and_then(|s| s.to_str()).unwrap_or("").to_string()
}

// ── Collection lifecycle ────────────────────────────────────────────────

/// Create a fresh collection scaffold at `root`.
pub fn init_collection(root: &str, name: &str) -> Result<(), String> {
    let root = PathBuf::from(root);
    fs::create_dir_all(&root).map_err(|e| e.to_string())?;
    fs::create_dir_all(root.join(ENV_DIR)).map_err(|e| e.to_string())?;
    let meta = serde_json::json!({ "name": name, "schema": 1 });
    let json = serde_json::to_string_pretty(&meta).map_err(|e| e.to_string())?;
    fs::write(root.join(META_FILE), json).map_err(|e| e.to_string())
}

/// Build the request tree for the sidebar (excludes meta + environments dir).
pub fn read_tree(root: &str) -> Result<TreeNode, String> {
    let path = PathBuf::from(root);
    if !path.is_dir() {
        return Err(format!("Not a folder: {root}"));
    }
    let name = read_meta_name(&path).unwrap_or_else(|| dir_name(&path));
    let mut node = build_dir_node(&path)?;
    node.name = name;
    Ok(node)
}

fn read_meta_name(root: &Path) -> Option<String> {
    let s = fs::read_to_string(root.join(META_FILE)).ok()?;
    let v: serde_json::Value = serde_json::from_str(&s).ok()?;
    v.get("name").and_then(|n| n.as_str()).map(|s| s.to_string())
}

fn build_dir_node(dir: &Path) -> Result<TreeNode, String> {
    let mut children = Vec::new();
    let mut entries: Vec<_> = fs::read_dir(dir)
        .map_err(|e| e.to_string())?
        .filter_map(|e| e.ok())
        .map(|e| e.path())
        .collect();
    entries.sort();

    for p in entries {
        if p.is_dir() {
            if dir_name(&p) == ENV_DIR { continue; }
            children.push(build_dir_node(&p)?);
        } else if is_request_file(&p) {
            let method = read_request(p.to_str().unwrap_or(""))
                .ok()
                .map(|r| r.method);
            children.push(TreeNode {
                name: file_stem(&p),
                path: p.to_string_lossy().to_string(),
                is_dir: false,
                method,
                children: vec![],
            });
        }
    }
    // Folders first, then requests, each alphabetical.
    children.sort_by(|a, b| match (a.is_dir, b.is_dir) {
        (true, false) => std::cmp::Ordering::Less,
        (false, true) => std::cmp::Ordering::Greater,
        _ => a.name.to_lowercase().cmp(&b.name.to_lowercase()),
    });

    Ok(TreeNode {
        name: dir_name(dir),
        path: dir.to_string_lossy().to_string(),
        is_dir: true,
        method: None,
        children,
    })
}

// ── Request CRUD ────────────────────────────────────────────────────────

pub fn read_request(path: &str) -> Result<RequestFile, String> {
    let s = fs::read_to_string(path).map_err(|e| e.to_string())?;
    serde_json::from_str(&s).map_err(|e| e.to_string())
}

/// Write a request into `dir` as `<name>.ohy` (sanitised), returns full path.
pub fn save_request(dir: &str, mut req: RequestFile) -> Result<String, String> {
    let dir = PathBuf::from(dir);
    fs::create_dir_all(&dir).map_err(|e| e.to_string())?;
    if req.name.trim().is_empty() {
        req.name = "untitled".into();
    }
    req.kind = "request".into();
    let file = dir.join(format!("{}.{EXT}", sanitize(&req.name)));
    let json = serde_json::to_string_pretty(&req).map_err(|e| e.to_string())?;
    fs::write(&file, json).map_err(|e| e.to_string())?;
    Ok(file.to_string_lossy().to_string())
}

/// Overwrite an existing request file at `path`.
pub fn write_request(path: &str, mut req: RequestFile) -> Result<(), String> {
    req.kind = "request".into();
    let json = serde_json::to_string_pretty(&req).map_err(|e| e.to_string())?;
    fs::write(path, json).map_err(|e| e.to_string())
}

pub fn delete_entry(path: &str) -> Result<(), String> {
    let p = PathBuf::from(path);
    if p.is_dir() {
        fs::remove_dir_all(&p).map_err(|e| e.to_string())
    } else {
        fs::remove_file(&p).map_err(|e| e.to_string())
    }
}

pub fn create_folder(parent: &str, name: &str) -> Result<String, String> {
    let p = PathBuf::from(parent).join(sanitize(name));
    fs::create_dir_all(&p).map_err(|e| e.to_string())?;
    Ok(p.to_string_lossy().to_string())
}

/// Create a fresh untitled request in `dir`, picking a unique name. Returns its path.
pub fn new_blank_request(dir: &str) -> Result<String, String> {
    let dirp = PathBuf::from(dir);
    fs::create_dir_all(&dirp).map_err(|e| e.to_string())?;
    let base = "Untitled";
    let mut name = base.to_string();
    let mut i = 2;
    while dirp.join(format!("{name}.{EXT}")).exists() {
        name = format!("{base} {i}");
        i += 1;
    }
    let req = RequestFile {
        kind: "request".into(),
        name: name.clone(),
        url: String::new(),
        method: "GET".into(),
        headers: HashMap::new(),
        body: String::new(),
        mode: "continuous".into(),
        interval: "5".into(),
        count: "10".into(),
        start_time: String::new(),
        stop_time: "23:59".into(),
    };
    save_request(dir, req)
}

/// Rename a request/folder in place. Returns the new path.
pub fn rename_entry(path: &str, new_name: &str) -> Result<String, String> {
    let p = PathBuf::from(path);
    let parent = p.parent().ok_or("No parent directory")?;
    let clean = sanitize(new_name);
    let dest = if p.is_dir() {
        parent.join(&clean)
    } else {
        parent.join(format!("{clean}.{EXT}"))
    };
    if dest == p {
        return Ok(path.to_string());
    }
    if dest.exists() {
        return Err("An entry with that name already exists".into());
    }
    fs::rename(&p, &dest).map_err(|e| e.to_string())?;
    // Keep the request file's internal `name` in sync.
    if dest.is_file() {
        let dest_str = dest.to_string_lossy().to_string();
        if let Ok(mut req) = read_request(&dest_str) {
            req.name = clean;
            let _ = write_request(&dest_str, req);
        }
    }
    Ok(dest.to_string_lossy().to_string())
}

/// Move a request/folder `from` into the directory `dest_dir`. Returns new path.
pub fn move_entry(from: &str, dest_dir: &str) -> Result<String, String> {
    let from = PathBuf::from(from);
    let dest_dir = PathBuf::from(dest_dir);
    if !dest_dir.is_dir() {
        return Err("Destination is not a folder".into());
    }
    let name = from.file_name().ok_or("Invalid source")?;
    let dest = dest_dir.join(name);

    // No-op if already in the destination folder.
    if from.parent() == Some(dest_dir.as_path()) {
        return Ok(from.to_string_lossy().to_string());
    }
    // Prevent moving a folder into itself or one of its descendants.
    if dest_dir.starts_with(&from) {
        return Err("Cannot move a folder into itself".into());
    }
    if dest.exists() {
        return Err("An entry with that name already exists there".into());
    }
    fs::rename(&from, &dest).map_err(|e| e.to_string())?;
    Ok(dest.to_string_lossy().to_string())
}

// ── Environments ────────────────────────────────────────────────────────

fn env_dir(root: &str) -> PathBuf {
    PathBuf::from(root).join(ENV_DIR)
}

pub fn list_environments(root: &str) -> Vec<Environment> {
    let dir = env_dir(root);
    let mut out = Vec::new();
    if let Ok(rd) = fs::read_dir(&dir) {
        for p in rd.filter_map(|e| e.ok()).map(|e| e.path()) {
            if is_request_file(&p) {
                if let Ok(s) = fs::read_to_string(&p) {
                    if let Ok(env) = serde_json::from_str::<Environment>(&s) {
                        out.push(env);
                    }
                }
            }
        }
    }
    out.sort_by(|a, b| a.name.to_lowercase().cmp(&b.name.to_lowercase()));
    out
}

pub fn save_environment(root: &str, env: Environment) -> Result<(), String> {
    let dir = env_dir(root);
    fs::create_dir_all(&dir).map_err(|e| e.to_string())?;
    let file = dir.join(format!("{}.{EXT}", sanitize(&env.name)));
    let json = serde_json::to_string_pretty(&env).map_err(|e| e.to_string())?;
    fs::write(file, json).map_err(|e| e.to_string())
}

pub fn delete_environment(root: &str, name: &str) -> Result<(), String> {
    let file = env_dir(root).join(format!("{}.{EXT}", sanitize(name)));
    if file.exists() {
        fs::remove_file(file).map_err(|e| e.to_string())?;
    }
    Ok(())
}

// ── Import / Export ─────────────────────────────────────────────────────

/// Build a bundle for `root` and write it as JSON to `dest`.
pub fn export_collection(root: &str, dest: &str) -> Result<(), String> {
    let path = PathBuf::from(root);
    let name = read_meta_name(&path).unwrap_or_else(|| dir_name(&path));
    let bundle = Bundle {
        name,
        root: build_bundle_node(&path)?,
        environments: list_environments(root),
    };
    let json = serde_json::to_string_pretty(&bundle).map_err(|e| e.to_string())?;
    fs::write(dest, json).map_err(|e| e.to_string())
}

fn build_bundle_node(dir: &Path) -> Result<BundleNode, String> {
    let mut children = Vec::new();
    if let Ok(rd) = fs::read_dir(dir) {
        for p in rd.filter_map(|e| e.ok()).map(|e| e.path()) {
            if p.is_dir() {
                if dir_name(&p) == ENV_DIR { continue; }
                children.push(build_bundle_node(&p)?);
            } else if is_request_file(&p) {
                if let Ok(req) = read_request(p.to_str().unwrap_or("")) {
                    children.push(BundleNode {
                        name: file_stem(&p),
                        is_dir: false,
                        request: Some(req),
                        children: vec![],
                    });
                }
            }
        }
    }
    Ok(BundleNode {
        name: dir_name(dir),
        is_dir: true,
        request: None,
        children,
    })
}

/// Read a bundle file and reconstruct it under `dest_parent/<bundle.name>`.
pub fn import_collection(file: &str, dest_parent: &str) -> Result<String, String> {
    let s = fs::read_to_string(file).map_err(|e| e.to_string())?;
    let bundle: Bundle = serde_json::from_str(&s).map_err(|e| e.to_string())?;
    let root = PathBuf::from(dest_parent).join(sanitize(&bundle.name));
    fs::create_dir_all(&root).map_err(|e| e.to_string())?;
    init_collection(root.to_str().unwrap_or(""), &bundle.name)?;
    write_bundle_children(&root, &bundle.root.children)?;
    let root_str = root.to_string_lossy().to_string();
    for env in bundle.environments {
        save_environment(&root_str, env)?;
    }
    Ok(root_str)
}

fn write_bundle_children(dir: &Path, nodes: &[BundleNode]) -> Result<(), String> {
    for node in nodes {
        if node.is_dir {
            let sub = dir.join(sanitize(&node.name));
            fs::create_dir_all(&sub).map_err(|e| e.to_string())?;
            write_bundle_children(&sub, &node.children)?;
        } else if let Some(req) = &node.request {
            save_request(dir.to_str().unwrap_or(""), req.clone())?;
        }
    }
    Ok(())
}

// ── Helpers ─────────────────────────────────────────────────────────────

fn sanitize(name: &str) -> String {
    let cleaned: String = name
        .chars()
        .map(|c| if "/\\:*?\"<>|".contains(c) { '-' } else { c })
        .collect();
    let trimmed = cleaned.trim();
    if trimmed.is_empty() { "untitled".into() } else { trimmed.to_string() }
}
