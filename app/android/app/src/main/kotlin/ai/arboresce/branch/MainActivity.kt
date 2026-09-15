package ai.arboresce.branch
import ai.arboresce.branch.ui.DiagnosticScreen
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import androidx.lifecycle.viewmodel.compose.viewModel

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContent {
            val model: RuntimeViewModel = viewModel()
            DiagnosticScreen(model.snapshot.collectAsStateWithLifecycle().value)
        }
    }
}
