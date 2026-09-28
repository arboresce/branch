package ai.arboresce.branch.ui

sealed interface DiagnosticPhase {
    data object Loading : DiagnosticPhase

    data class Content(
        val text: String,
    ) : DiagnosticPhase

    data class Error(
        val message: String,
    ) : DiagnosticPhase
}
