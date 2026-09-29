package ai.arboresce.branch.catalog.host

import androidx.compose.ui.test.assertIsDisplayed
import androidx.compose.ui.test.hasTestTag
import androidx.compose.ui.test.junit4.createAndroidComposeRule
import androidx.compose.ui.test.onNodeWithTag
import androidx.compose.ui.test.performClick
import androidx.compose.ui.test.performScrollToNode
import org.junit.Rule
import org.junit.Test

class CatalogScreenTest {
    @get:Rule val compose = createAndroidComposeRule<CatalogActivity>()

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
}
