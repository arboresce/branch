#![forbid(unsafe_code)]
use branch_domain::AppState;
use serde::Serialize;
use std::sync::Mutex;

#[derive(Debug, PartialEq, Eq)]
pub enum Error {
    Closed,
    Unavailable,
    Serialization,
}
#[derive(Serialize)]
struct Metadata {
    name: &'static str,
    version: &'static str,
    core_version: &'static str,
    os: &'static str,
    architecture: &'static str,
    target: &'static str,
    rustc: &'static str,
    profile: &'static str,
    build_id: &'static str,
    authentication: &'static str,
    network: &'static str,
    persistence: &'static str,
    sync: &'static str,
}
#[derive(Serialize)]
struct Snapshot<'a> {
    schema_version: u32,
    revision: u64,
    state: &'a AppState,
    runtime: Metadata,
}
pub struct Runtime {
    state: Mutex<Option<AppState>>,
}
impl Default for Runtime {
    fn default() -> Self {
        Self {
            state: Mutex::new(Some(AppState::default())),
        }
    }
}
impl Runtime {
    pub fn snapshot_json(&self) -> Result<String, Error> {
        let guard = self.state.lock().map_err(|_| Error::Unavailable)?;
        let state = guard.as_ref().ok_or(Error::Closed)?;
        serde_json::to_string_pretty(&Snapshot {
            schema_version: 1,
            revision: 0,
            state,
            runtime: Metadata {
                name: "branch-by-arboresce",
                version: env!("CARGO_PKG_VERSION"),
                core_version: branch_domain::VERSION,
                os: std::env::consts::OS,
                architecture: std::env::consts::ARCH,
                target: env!("BRANCH_TARGET"),
                rustc: env!("BRANCH_RUSTC"),
                profile: env!("BRANCH_PROFILE"),
                build_id: option_env!("BRANCH_BUILD_ID").unwrap_or("unpackaged"),
                authentication: "not_configured",
                network: "not_configured",
                persistence: "not_configured",
                sync: "not_configured",
            },
        })
        .map_err(|_| Error::Serialization)
    }
    pub fn close(&self) -> Result<(), Error> {
        *self.state.lock().map_err(|_| Error::Unavailable)? = None;
        Ok(())
    }
}
#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn snapshot_contains_actual_build_and_preview_state() {
        let runtime = Runtime::default();
        let data: serde_json::Value =
            serde_json::from_str(&runtime.snapshot_json().unwrap()).unwrap();
        assert_eq!(data["schema_version"], 1);
        assert_eq!(data["runtime"]["name"], "branch-by-arboresce");
        assert_eq!(data["runtime"]["os"], std::env::consts::OS);
        assert!(
            data["runtime"]["rustc"]
                .as_str()
                .unwrap()
                .starts_with("rustc ")
        );
        assert_eq!(data["state"]["session_mode"], "preview");
        assert!(data["state"]["user"].is_null());
        assert!(runtime.snapshot_json().unwrap().len() < 8192);
    }
    #[test]
    fn close_is_idempotent_and_terminal() {
        let runtime = Runtime::default();
        runtime.close().unwrap();
        runtime.close().unwrap();
        assert_eq!(runtime.snapshot_json(), Err(Error::Closed));
    }
    #[test]
    fn concurrent_reads_are_stable() {
        let runtime = std::sync::Arc::new(Runtime::default());
        let expected = runtime.snapshot_json().unwrap();
        let readers: Vec<_> = (0..8)
            .map(|_| {
                let runtime = runtime.clone();
                std::thread::spawn(move || runtime.snapshot_json().unwrap())
            })
            .collect();
        for reader in readers {
            assert_eq!(reader.join().unwrap(), expected);
        }
    }
}
