package ai.arboresce.branch.shared

import ai.arboresce.branch.ui.DiagnosticScreen
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue

@Composable
fun AppRoot(controller: RuntimeController) {
    val phase by controller.phase.collectAsState()
    DiagnosticScreen(phase = phase, onRetry = controller::load)
}
