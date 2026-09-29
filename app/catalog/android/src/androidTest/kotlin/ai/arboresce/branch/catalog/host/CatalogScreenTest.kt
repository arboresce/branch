package ai.arboresce.branch.catalog.host

import androidx.compose.ui.test.assertIsDisplayed
import androidx.compose.ui.test.junit4.createAndroidComposeRule
import androidx.compose.ui.test.onNodeWithTag
import org.junit.Rule
import org.junit.Test

class CatalogScreenTest {
    @get:Rule val compose = createAndroidComposeRule<CatalogActivity>()

    @Test
    fun catalogRendersFixedFixtures() {
        compose.onNodeWithTag("catalog-title").assertIsDisplayed()
        compose.onNodeWithTag("catalog-clock").assertIsDisplayed()
        compose.onNodeWithTag("catalog-item-1").assertIsDisplayed()
        compose.onNodeWithTag("catalog-item-5").assertIsDisplayed()
    }
}
