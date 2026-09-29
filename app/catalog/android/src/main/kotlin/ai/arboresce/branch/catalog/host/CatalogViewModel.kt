package ai.arboresce.branch.catalog.host

import ai.arboresce.branch.catalog.ScriptedRuntimeSource
import ai.arboresce.branch.shared.RuntimeController
import ai.arboresce.branch.shared.createRuntimeController
import androidx.lifecycle.ViewModel

/**
 * Retained owner of the catalog controller. It survives configuration changes so the
 * same controller renders across recreation, and disposes terminally only when the
 * ViewModel is cleared (the owner is removed).
 */
class CatalogViewModel : ViewModel() {
    val controller: RuntimeController = createRuntimeController(ScriptedRuntimeSource())

    override fun onCleared() {
        controller.dispose()
    }
}
