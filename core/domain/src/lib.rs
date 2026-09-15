#![forbid(unsafe_code)]
use serde::Serialize;

pub const VERSION: &str = env!("CARGO_PKG_VERSION");
#[derive(Debug, Clone, PartialEq, Eq, Serialize)]
pub struct UserContext {
    pub display_name: String,
}
#[derive(Debug, Clone, PartialEq, Eq, Serialize)]
pub struct WorkspaceContext {
    pub name: String,
}
#[derive(Debug, Clone, PartialEq, Eq, Serialize)]
#[serde(rename_all = "snake_case")]
pub enum SessionMode {
    Preview,
}
#[derive(Debug, Clone, PartialEq, Eq, Serialize)]
pub struct AppState {
    pub session_mode: SessionMode,
    pub user: Option<UserContext>,
    pub workspace: Option<WorkspaceContext>,
}
impl Default for AppState {
    fn default() -> Self {
        Self {
            session_mode: SessionMode::Preview,
            user: None,
            workspace: None,
        }
    }
}
#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn preview_does_not_fabricate_an_account() {
        let state = AppState::default();
        assert_eq!(state.session_mode, SessionMode::Preview);
        assert!(state.user.is_none() && state.workspace.is_none());
    }
}
