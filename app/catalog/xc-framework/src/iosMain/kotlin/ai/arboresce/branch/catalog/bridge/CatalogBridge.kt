package ai.arboresce.branch.catalog.bridge

import ai.arboresce.branch.catalog.CatalogFixtures
import ai.arboresce.branch.catalog.CatalogRoot
import ai.arboresce.branch.catalog.ScriptedRuntimeSource
import ai.arboresce.branch.shared.RuntimeController
import ai.arboresce.branch.shared.createRuntimeController
import androidx.compose.ui.window.ComposeUIViewController

fun createCatalogController(): RuntimeController = createRuntimeController(ScriptedRuntimeSource())

fun makeCatalogViewController(controller: RuntimeController) = ComposeUIViewController { CatalogRoot(controller) }

fun catalogItemTitles(): List<String> = CatalogFixtures.items.map { it.title }
