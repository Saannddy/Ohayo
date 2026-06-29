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

    // Cap response body to bound memory (256 KB).
    const MAX_BODY: usize = 256 * 1024;

    match req.send().await {
        Ok(resp) => {
            let status = resp.status().as_u16();
            let resp_headers: HashMap<String, String> = resp
                .headers()
                .iter()
                .map(|(k, v)| (k.to_string(), v.to_str().unwrap_or("").to_string()))
                .collect();
            // Latency reflects time-to-headers, before draining the body.
            let elapsed_ms = elapsed();
            let raw = resp.text().await.unwrap_or_default();
            let body = if raw.len() > MAX_BODY {
                let mut end = MAX_BODY;
                while !raw.is_char_boundary(end) { end -= 1; }
                format!("{}… [truncated]", &raw[..end])
            } else {
                raw
            };
            RequestResult::Success(ResponsePayload {
                timestamp: ts,
                count: request_count,
                method: method.to_string(),
                status,
                elapsed_ms,
                url: url.to_string(),
                body,
                headers: resp_headers,
            })
        }
        Err(e) => RequestResult::Failure(ErrorPayload {
            timestamp: ts,
            count: request_count,
            error: if e.is_timeout() { "Timed out (10s)".into() } else { e.to_string() },
            elapsed_ms: elapsed(),
        }),
    }
}
