package ai.arboresce.branch.ui

import androidx.compose.foundation.background
import androidx.compose.foundation.horizontalScroll
import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.fillMaxSize
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
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp

@Composable
fun DiagnosticScreen(snapshot: String) {
    val dark = isSystemInDarkTheme()
    Box(
        Modifier
            .fillMaxSize()
            .background(if (dark) Color(0xFF1C1E22) else Color.White)
            .safeDrawingPadding(),
    ) {
        SelectionContainer {
            BasicText(
                text = snapshot,
                modifier =
                    Modifier
                        .fillMaxSize()
                        .verticalScroll(rememberScrollState())
                        .horizontalScroll(rememberScrollState())
                        .padding(16.dp)
                        .testTag("runtime-snapshot"),
                style =
                    TextStyle(
                        color = if (dark) Color.White else Color(0xFF1C1E22),
                        fontFamily = FontFamily.Monospace,
                        fontSize = 13.sp,
                    ),
            )
        }
    }
}
