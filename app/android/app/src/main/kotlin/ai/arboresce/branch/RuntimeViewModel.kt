package ai.arboresce.branch
import android.app.Application
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

class RuntimeViewModel(
    application: Application,
) : AndroidViewModel(application) {
    private val text = MutableStateFlow("Loading runtime…")
    val snapshot = text.asStateFlow()

    init {
        viewModelScope.launch(Dispatchers.Default) {
            text.value =
                try {
                    (application as BranchApplication).runtime.snapshotJson()
                } catch (
                    _: Exception,
                ) {
                    "{\"error\": \"runtime_unavailable\"}"
                }
        }
    }
}
