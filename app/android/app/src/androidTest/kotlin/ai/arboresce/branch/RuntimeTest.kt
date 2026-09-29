package ai.arboresce.branch

import androidx.compose.ui.semantics.SemanticsProperties
import androidx.compose.ui.test.assertIsDisplayed
import androidx.compose.ui.test.assertTextContains
import androidx.compose.ui.test.hasTestTag
import androidx.compose.ui.test.junit4.createAndroidComposeRule
import androidx.compose.ui.test.onNodeWithTag
import androidx.lifecycle.Lifecycle
import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Rule
import org.junit.Test

class RuntimeTest {
    @get:Rule val compose = createAndroidComposeRule<MainActivity>()

    private fun snapshotText(): String? =
        compose
            .onAllNodes(hasTestTag("runtime-snapshot"))
            .fetchSemanticsNodes()
            .firstOrNull()
            ?.config
            ?.get(SemanticsProperties.Text)
            ?.joinToString()

    @Test
    fun homeDisplaysRealRustState() {
        val app = compose.activity.applicationInfo
        assertEquals("branch", app.loadLabel(compose.activity.packageManager).toString())
        assertTrue(app.icon != 0)
        compose.waitUntil(15000) { snapshotText()?.contains("schema_version") == true }
        compose
            .onNodeWithTag("runtime-snapshot")
            .assertTextContains("branch-by-arboresce", substring = true)
        compose
            .onNodeWithTag("runtime-snapshot")
            .assertTextContains("android", substring = true)
        compose.onNodeWithTag("runtime-snapshot").assertTextContains("rustc", substring = true)
    }

    @Test
    fun homeResumesWithVisibleContentAfterBackgroundStop() {
        compose.waitUntil(15000) { snapshotText()?.contains("schema_version") == true }
        compose.activityRule.scenario.moveToState(Lifecycle.State.CREATED)
        compose.activityRule.scenario.moveToState(Lifecycle.State.RESUMED)
        compose.waitUntil(15000) { snapshotText()?.contains("schema_version") == true }
        compose.onNodeWithTag("runtime-snapshot").assertIsDisplayed()
    }
}
