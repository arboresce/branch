package ai.arboresce.branch

import ai.arboresce.branch.shared.RuntimeController
import ai.arboresce.branch.shared.RuntimeSource
import android.app.Application
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope

class RuntimeViewModel(
    application: Application,
) : AndroidViewModel(application) {
    val controller =
        RuntimeController(
            object : RuntimeSource {
                override fun snapshot(): String? =
                    try {
                        (application as BranchApplication).runtime.snapshotJson()
                    } catch (
                        _: Exception,
                    ) {
                        null
                    }
            },
            viewModelScope,
        )

    init {
        controller.load()
    }

    override fun onCleared() {
        controller.dispose()
    }
}
