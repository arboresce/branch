package ai.arboresce.branch.catalog.host

import android.graphics.Bitmap
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.toPixelMap
import androidx.compose.ui.semantics.SemanticsProperties
import androidx.compose.ui.test.assertIsDisplayed
import androidx.compose.ui.test.captureToImage
import androidx.compose.ui.test.hasTestTag
import androidx.compose.ui.test.junit4.createAndroidComposeRule
import androidx.compose.ui.test.onNodeWithTag
import androidx.compose.ui.test.performClick
import androidx.compose.ui.test.performScrollToNode
import androidx.lifecycle.Lifecycle
import androidx.test.platform.app.InstrumentationRegistry
import org.junit.Assert.assertEquals
import org.junit.Assert.assertNotEquals
import org.junit.Rule
import org.junit.Test
import java.io.File

class CatalogScreenTest {
    @get:Rule val compose = createAndroidComposeRule<CatalogActivity>()

    private fun diagnosticText(): String? =
        compose
            .onAllNodes(hasTestTag("runtime-snapshot"))
            .fetchSemanticsNodes()
            .firstOrNull()
            ?.config
            ?.get(SemanticsProperties.Text)
            ?.joinToString()

    @Test
    fun catalogRendersFixedFixtures() {
        compose.onNodeWithTag("catalog-title").assertIsDisplayed()
        compose.onNodeWithTag("catalog-list").performScrollToNode(hasTestTag("catalog-item-1"))
        compose.onNodeWithTag("catalog-item-1").assertIsDisplayed()
    }

    @Test
    fun navigationProbeTransitionsBetweenTwoEntries() {
        compose.onNodeWithTag("catalog-list").performScrollToNode(hasTestTag("nav3-home"))
        compose.onNodeWithTag("nav3-push").performClick()
        compose.onNodeWithTag("nav3-detail").assertIsDisplayed()
    }

    @Test
    fun imageProbeResolvesDeterministicSuccessAndError() {
        compose.onNodeWithTag("catalog-list").performScrollToNode(hasTestTag("image-probe"))
        compose.waitUntil(20_000) {
            compose.onAllNodes(hasTestTag("image-success")).fetchSemanticsNodes().isNotEmpty()
        }
        compose.onNodeWithTag("image-success").assertIsDisplayed()
        compose.onNodeWithTag("image-error").assertIsDisplayed()
    }

    @Test
    fun catalogOnlyResourceRenders() {
        compose.onNodeWithTag("catalog-resource").assertExists()
    }

    @Test
    fun glassProbeRendersLiveSurfaceAndBothFallbacks() {
        compose.onNodeWithTag("glass-surface").assertExists()
        compose.onNodeWithTag("glass-fallback-capability").assertExists()
        compose.onNodeWithTag("glass-fallback-effects").assertExists()
        val list = compose.onNodeWithTag("catalog-list")
        for (tag in listOf("glass-surface", "glass-fallback-capability", "glass-fallback-effects")) {
            list.performScrollToNode(hasTestTag("$tag-box"))
            captureScreen(tag)
        }
    }

    private fun captureScreen(name: String) {
        val instrumentation = InstrumentationRegistry.getInstrumentation()
        val bitmap = instrumentation.uiAutomation.takeScreenshot()
        val directory = instrumentation.targetContext.getExternalFilesDir(null) ?: return
        File(directory, "$name.png").outputStream().use {
            bitmap.compress(Bitmap.CompressFormat.PNG, 100, it)
        }
    }

    @Test
    fun fallbackSurfaceRendersTheReadableBackground() {
        val list = compose.onNodeWithTag("catalog-list")
        list.performScrollToNode(hasTestTag("glass-fallback-capability-box"))
        val pixel =
            compose
                .onNodeWithTag("glass-fallback-capability-box")
                .captureToImage()
                .toPixelMap()[2, 2]
        assertEquals(Color(0xFF22242A), pixel)
    }

    @Test
    fun liveSurfaceUsesHostCapabilityInsteadOfTheFallback() {
        val list = compose.onNodeWithTag("catalog-list")
        list.performScrollToNode(hasTestTag("glass-surface-box"))
        val pixel =
            compose.onNodeWithTag("glass-surface-box").captureToImage().toPixelMap()[2, 2]
        assertNotEquals(Color(0xFF22242A), pixel)
    }

    @Test
    fun diagnosticUpdatesInPlaceAndResumesAfterBackground() {
        compose.waitUntil(20_000) { diagnosticText()?.contains("\"revision\"") == true }
        compose.onNodeWithTag("diagnostic-next").performClick()
        compose.waitUntil(20_000) { diagnosticText()?.contains("\"revision\":1") == true }
        compose.activityRule.scenario.moveToState(Lifecycle.State.CREATED)
        compose.activityRule.scenario.moveToState(Lifecycle.State.RESUMED)
        compose.waitUntil(20_000) { diagnosticText()?.contains("\"revision\"") == true }
    }
}
