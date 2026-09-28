package ai.arboresce.branch.ui

import ai.arboresce.branch.shared.AppRoot
import ai.arboresce.branch.shared.RuntimeController
import ai.arboresce.branch.shared.RuntimeSource
import ai.arboresce.branch.shared.createRuntimeController
import androidx.compose.ui.window.ComposeUIViewController

fun makeDiagnosticViewController(controller: RuntimeController) = ComposeUIViewController { AppRoot(controller) }

fun createDiagnosticController(source: RuntimeSource): RuntimeController = createRuntimeController(source)

fun diagnosticPhaseKind(controller: RuntimeController): String =
    when (controller.phase.value) {
        DiagnosticPhase.Loading -> "loading"
        is DiagnosticPhase.Content -> "content"
        is DiagnosticPhase.Error -> "error"
    }

fun diagnosticContent(controller: RuntimeController): String? = (controller.phase.value as? DiagnosticPhase.Content)?.text
