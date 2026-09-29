package ai.arboresce.branch.catalog

import ai.arboresce.branch.catalog.resources.Res
import ai.arboresce.branch.catalog.resources.catalog_probe_label
import ai.arboresce.branch.shared.AppRoot
import ai.arboresce.branch.shared.RuntimeController
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.WindowInsets
import androidx.compose.foundation.layout.consumeWindowInsets
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.safeDrawing
import androidx.compose.foundation.layout.windowInsetsPadding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.text.BasicText
import androidx.compose.runtime.Composable
import androidx.compose.runtime.remember
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.unit.dp
import org.jetbrains.compose.resources.stringResource

/**
 * Catalog consumer of the shared modules. The hosting application owns [controller] and
 * its lifecycle; the composable only renders it so background/resume and terminal
 * disposal stay with the real host.
 */
@Composable
fun CatalogRoot(controller: RuntimeController) {
    val clock = remember { FixedCatalogClock() }
    val insets = WindowInsets.safeDrawing
    Column(Modifier.fillMaxSize().windowInsetsPadding(insets).consumeWindowInsets(insets)) {
        BasicText("Catalog", Modifier.testTag("catalog-title"))
        BasicText("clock=${clock.nowMillis()}", Modifier.testTag("catalog-clock"))
        BasicText(
            stringResource(Res.string.catalog_probe_label),
            Modifier.testTag("catalog-resource"),
        )
        Box(Modifier.height(120.dp)) { AppRoot(controller) }
        BasicText(
            "Advance diagnostic",
            Modifier.testTag("diagnostic-next").clickable {
                controller.cancel()
                controller.load()
            },
        )
        LazyColumn(Modifier.weight(1f).testTag("catalog-list")) {
            item { CatalogImageProbe() }
            item { CatalogNavigationProbe() }
            item { CatalogGlassGallery() }
            items(CatalogFixtures.items, key = { it.id }) { item ->
                BasicText(
                    "${item.id} | ${item.title} | ${item.subtitle}",
                    Modifier.testTag(item.id),
                )
            }
        }
    }
}
