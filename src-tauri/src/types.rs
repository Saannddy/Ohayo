use serde::{Deserialize, Serialize};
use std::collections::HashMap;

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct ScheduleConfig {
    pub url: String,
    pub method: String,
    pub headers: HashMap<String, String>,
    pub body: String,
    pub mode: String,
    pub interval: u64,
    pub count: u32,
    #[serde(default)]
    pub start_time: String,
    pub stop_time: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct ResponsePayload {
    pub timestamp: String,
    pub count: u32,
    pub method: String,
    pub status: u16,
    pub elapsed_ms: f64,
    pub url: String,
    pub body: String,
    pub headers: HashMap<String, String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct ErrorPayload {
    pub timestamp: String,
    pub count: u32,
    pub error: String,
    pub elapsed_ms: f64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct CountdownPayload {
    pub remaining: u64,
    pub total: u64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct SentPayload {
    pub count: u32,
    pub target: Option<u32>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct StatsPayload {
    pub total: u32,
    pub success: u32,
    pub success_pct: f64,
    pub avg_ms: f64,
    pub last_status: Option<u16>,
}

/// A single saved request, stored as one `.ohy` file inside a collection folder.
#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct RequestFile {
    #[serde(default = "default_kind")]
    pub kind: String,
    #[serde(default)]
    pub name: String,
    pub url: String,
    pub method: String,
    pub headers: HashMap<String, String>,
    pub body: String,
    pub mode: String,
    pub interval: String,
    pub count: String,
    #[serde(default)]
    pub start_time: String,
    pub stop_time: String,
}

fn default_kind() -> String { "request".into() }

/// A node in the collection tree handed to the frontend.
#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct TreeNode {
    pub name: String,
    pub path: String,
    pub is_dir: bool,
    pub method: Option<String>,
    pub children: Vec<TreeNode>,
}

/// A named set of variables, stored as one file under `environments/`.
#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct Environment {
    pub name: String,
    pub vars: HashMap<String, String>,
}

/// Self-contained export of a whole collection (tree + environments).
#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct Bundle {
    pub name: String,
    pub root: BundleNode,
    pub environments: Vec<Environment>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct BundleNode {
    pub name: String,
    pub is_dir: bool,
    pub request: Option<RequestFile>,
    pub children: Vec<BundleNode>,
}
