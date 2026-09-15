package ai.arboresce.branch
import androidx.compose.ui.semantics.SemanticsProperties
import androidx.compose.ui.test.assertTextContains
import androidx.compose.ui.test.junit4.createAndroidComposeRule
import androidx.compose.ui.test.onNodeWithTag
import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Rule
import org.junit.Test

class RuntimeTest {
    @get:Rule val compose = createAndroidComposeRule<MainActivity>()

    @Test fun homeDisplaysRealRustState() {
        val app = compose.activity.applicationInfo
        assertEquals("branch", app.loadLabel(compose.activity.packageManager).toString())
        assertTrue(app.icon != 0)
        compose.waitUntil(15000) {
            compose
                .onNodeWithTag(
                    "runtime-snapshot",
                ).fetchSemanticsNode()
                .config[SemanticsProperties.Text]
                .joinToString()
                .contains("schema_version")
        }
        compose.onNodeWithTag("runtime-snapshot").assertTextContains("branch-by-arboresce", substring = true)
        compose.onNodeWithTag("runtime-snapshot").assertTextContains("android", substring = true)
        compose.onNodeWithTag("runtime-snapshot").assertTextContains("rustc", substring = true)
    }
}
