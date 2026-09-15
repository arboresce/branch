package ai.arboresce.branch.ui
import androidx.compose.ui.window.ComposeUIViewController

fun makeDiagnosticViewController(snapshot: String) = ComposeUIViewController { DiagnosticScreen(snapshot) }
