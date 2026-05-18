use std::collections::HashMap;
use std::time::Instant;
use chrono::Local;
use reqwest::Client;
use crate::types::{ResponsePayload, ErrorPayload};

pub enum RequestResult {
    Success(ResponsePayload),
    Failure(ErrorPayload),
}

pub async fn make_request(
    client: &Client,
    url: &str,
    method: &str,
    headers: &HashMap<String, String>,
    body: &str,
    request_count: u32,
) -> RequestResult {
    let ts = Local::now().format("%H:%M:%S").to_string();
    let start = Instant::now();

    let builder = match method {
        "POST"   => client.post(url),
        "PUT"    => client.put(url),
        "PATCH"  => client.patch(url),
        "DELETE" => client.delete(url),
        "HEAD"   => client.head(url),
        _        => client.get(url),
    };

    let mut req = builder.timeout(std::time::Duration::from_secs(10));

    for (k, v) in headers {
        req = req.header(k.as_str(), v.as_str());
    }

    let uses_body = matches!(method, "POST" | "PUT" | "PATCH");
    if uses_body && !body.is_empty() {
        req = req.body(body.to_string());
    }

    let elapsed = || start.elapsed().as_secs_f64() * 1000.0;

    match req.send().await {
        Ok(resp) => RequestResult::Success(ResponsePayload {
            timestamp: ts,
            count: request_count,
            method: method.to_string(),
            status: resp.status().as_u16(),
            elapsed_ms: elapsed(),
            url: url.to_string(),
        }),
        Err(e) => RequestResult::Failure(ErrorPayload {
            timestamp: ts,
            count: request_count,
            error: if e.is_timeout() { "Timed out (10s)".into() } else { e.to_string() },
            elapsed_ms: elapsed(),
        }),
    }
}
