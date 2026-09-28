package ai.arboresce.branch

import ai.arboresce.branch.ui.DiagnosticPhase
import ai.arboresce.branch.ui.DiagnosticScreen
import androidx.compose.ui.test.assertIsDisplayed
import androidx.compose.ui.test.assertTextContains
import androidx.compose.ui.test.junit4.createComposeRule
import androidx.compose.ui.test.onNodeWithTag
import androidx.compose.ui.test.performClick
import org.junit.Assert.assertTrue
import org.junit.Rule
import org.junit.Test

class DiagnosticScreenTest {
    @get:Rule val compose = createComposeRule()

    @Test
    fun loadingPhaseShowsSharedLoadingState() {
        compose.setContent { DiagnosticScreen(DiagnosticPhase.Loading) {} }
        compose
            .onNodeWithTag("runtime-loading")
            .assertIsDisplayed()
            .assertTextContains("Loading runtime", substring = true)
    }

    @Test
    fun errorPhaseShowsSanitizedMessageAndRetries() {
        var retried = false
        compose.setContent {
            DiagnosticScreen(DiagnosticPhase.Error("Runtime unavailable")) { retried = true }
        }
        compose.onNodeWithTag("runtime-error").assertTextContains("Runtime unavailable")
        compose.onNodeWithTag("runtime-retry").performClick()
        assertTrue(retried)
    }
}
