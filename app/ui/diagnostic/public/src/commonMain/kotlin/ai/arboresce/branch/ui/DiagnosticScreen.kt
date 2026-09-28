package ai.arboresce.branch.ui

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.horizontalScroll
import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.safeDrawingPadding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.text.BasicText
import androidx.compose.foundation.text.selection.SelectionContainer
import androidx.compose.foundation.verticalScroll
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.semantics.Role
import androidx.compose.ui.semantics.role
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp

@Composable
fun DiagnosticScreen(
    phase: DiagnosticPhase,
    onRetry: () -> Unit,
) {
    val dark = isSystemInDarkTheme()
    val foreground = if (dark) Color.White else Color(0xFF1C1E22)
    val style = TextStyle(color = foreground, fontSize = 13.sp)
    Box(
        Modifier
            .fillMaxSize()
            .background(if (dark) Color(0xFF1C1E22) else Color.White)
            .safeDrawingPadding(),
    ) {
        when (phase) {
            DiagnosticPhase.Loading ->
                BasicText(
                    text = "Loading runtime…",
                    modifier = Modifier.fillMaxSize().padding(16.dp).testTag("runtime-loading"),
                    style = style,
                )

            is DiagnosticPhase.Error ->
                Column(Modifier.fillMaxSize().padding(16.dp)) {
                    BasicText(
                        text = phase.message,
                        modifier = Modifier.testTag("runtime-error"),
                        style = style,
                    )
                    Spacer(Modifier.height(8.dp))
                    BasicText(
                        text = "Retry",
                        modifier =
                            Modifier
                                .testTag("runtime-retry")
                                .clickable(onClick = onRetry)
                                .semantics { role = Role.Button },
                        style = style,
                    )
                }

            is DiagnosticPhase.Content ->
                SelectionContainer {
                    BasicText(
                        text = phase.text,
                        modifier =
                            Modifier
                                .fillMaxSize()
                                .verticalScroll(rememberScrollState())
                                .horizontalScroll(rememberScrollState())
                                .padding(16.dp)
                                .testTag("runtime-snapshot"),
                        style = style.copy(fontFamily = FontFamily.Monospace),
                    )
                }
        }
    }
}
