package ai.arboresce.branch.catalog

import ai.arboresce.branch.shared.AppRoot
import ai.arboresce.branch.shared.createRuntimeController
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.text.BasicText
import androidx.compose.runtime.Composable
import androidx.compose.runtime.DisposableEffect
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.remember
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.unit.dp

@Composable
fun CatalogRoot() {
    val controller = remember { createRuntimeController(ScriptedRuntimeSource()) }
    val clock = remember { FixedCatalogClock() }
    LaunchedEffect(controller) { controller.load() }
    DisposableEffect(controller) { onDispose { controller.dispose() } }
    Column(Modifier.fillMaxSize()) {
        BasicText("Catalog", Modifier.testTag("catalog-title"))
        BasicText("clock=${clock.nowMillis()}", Modifier.testTag("catalog-clock"))
        Box(Modifier.height(72.dp)) { AppRoot(controller) }
        LazyColumn(Modifier.weight(1f).testTag("catalog-list")) {
            item { CatalogNavigationProbe() }
            item { CatalogGlassProbe() }
            item { CatalogImageProbe() }
            items(CatalogFixtures.items, key = { it.id }) { item ->
                BasicText(
                    "${item.id} | ${item.title} | ${item.subtitle}",
                    Modifier.testTag(item.id),
                )
            }
        }
    }
}
