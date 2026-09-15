uniffi::setup_scaffolding!();
#[derive(Debug, uniffi::Error)]
pub enum RuntimeError {
    Closed,
    Unavailable,
    Serialization,
}
impl std::fmt::Display for RuntimeError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{self:?}")
    }
}
impl std::error::Error for RuntimeError {}
impl From<branch_runtime::Error> for RuntimeError {
    fn from(error: branch_runtime::Error) -> Self {
        match error {
            branch_runtime::Error::Closed => Self::Closed,
            branch_runtime::Error::Unavailable => Self::Unavailable,
            branch_runtime::Error::Serialization => Self::Serialization,
        }
    }
}
#[derive(uniffi::Object, Default)]
pub struct BranchRuntime {
    inner: branch_runtime::Runtime,
}
#[uniffi::export]
impl BranchRuntime {
    #[uniffi::constructor]
    pub fn new() -> Self {
        Self::default()
    }
    pub fn snapshot_json(&self) -> Result<String, RuntimeError> {
        self.inner.snapshot_json().map_err(Into::into)
    }
    pub fn shutdown(&self) -> Result<(), RuntimeError> {
        self.inner.close().map_err(Into::into)
    }
}
#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn bridge_reads_and_closes_the_owned_runtime() {
        let runtime = BranchRuntime::new();
        assert!(
            runtime
                .snapshot_json()
                .unwrap()
                .contains("branch-by-arboresce")
        );
        runtime.shutdown().unwrap();
        assert!(matches!(runtime.snapshot_json(), Err(RuntimeError::Closed)));
    }
}
