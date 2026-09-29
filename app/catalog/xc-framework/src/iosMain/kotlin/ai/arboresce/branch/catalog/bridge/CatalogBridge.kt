package ai.arboresce.branch.catalog.bridge

import ai.arboresce.branch.catalog.CatalogFixtures
import ai.arboresce.branch.catalog.CatalogRoot
import ai.arboresce.branch.catalog.ScriptedRuntimeSource
import ai.arboresce.branch.catalog.glassCapabilityAvailable
import ai.arboresce.branch.shared.RuntimeController
import ai.arboresce.branch.shared.createRuntimeController
import ai.arboresce.branch.ui.DiagnosticPhase
import androidx.compose.ui.window.ComposeUIViewController

fun createCatalogController(): RuntimeController = createRuntimeController(ScriptedRuntimeSource())

fun catalogGlassCapability(): Boolean = true

fun makeCatalogViewController(controller: RuntimeController) =
    ComposeUIViewController {
        CatalogRoot(controller, glassCapabilityAvailable = catalogGlassCapability())
    }

fun catalogItemTitles(): List<String> = CatalogFixtures.items.map { it.title }

fun catalogPhaseKind(controller: RuntimeController): String =
    when (controller.phase.value) {
        DiagnosticPhase.Loading -> "loading"
        is DiagnosticPhase.Content -> "content"
        is DiagnosticPhase.Error -> "error"
    }
