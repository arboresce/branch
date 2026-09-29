package ai.arboresce.branch.catalog.host

import androidx.compose.ui.semantics.SemanticsProperties
import androidx.compose.ui.test.assertIsDisplayed
import androidx.compose.ui.test.hasTestTag
import androidx.compose.ui.test.junit4.createAndroidComposeRule
import androidx.compose.ui.test.onNodeWithTag
import androidx.compose.ui.test.performClick
import androidx.compose.ui.test.performScrollToNode
import androidx.lifecycle.Lifecycle
import org.junit.Rule
import org.junit.Test

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
    fun diagnosticUpdatesInPlaceAndResumesAfterBackground() {
        compose.waitUntil(20_000) { diagnosticText()?.contains("\"revision\"") == true }
        compose.onNodeWithTag("diagnostic-next").performClick()
        compose.waitUntil(20_000) { diagnosticText()?.contains("\"revision\":1") == true }
        compose.activityRule.scenario.moveToState(Lifecycle.State.CREATED)
        compose.activityRule.scenario.moveToState(Lifecycle.State.RESUMED)
        compose.waitUntil(20_000) { diagnosticText()?.contains("\"revision\"") == true }
    }
}
