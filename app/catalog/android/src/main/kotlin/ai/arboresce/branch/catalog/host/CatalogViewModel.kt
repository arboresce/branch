package ai.arboresce.branch.catalog.host

import ai.arboresce.branch.catalog.ScriptedRuntimeSource
import ai.arboresce.branch.shared.RuntimeController
import ai.arboresce.branch.shared.createRuntimeController
import androidx.lifecycle.ViewModel

class CatalogViewModel : ViewModel() {
    val controller: RuntimeController = createRuntimeController(ScriptedRuntimeSource())

    override fun onCleared() {
        controller.dispose()
    }
}
