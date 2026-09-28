package ai.arboresce.branch.shared

import ai.arboresce.branch.ui.DiagnosticPhase
import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.CoroutineDispatcher
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.Job
import kotlinx.coroutines.MainScope
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext

class RuntimeController(
    private val source: RuntimeSource,
    private val scope: CoroutineScope,
    private val dispatcher: CoroutineDispatcher = Dispatchers.Default,
) {
    private val mutable = MutableStateFlow<DiagnosticPhase>(DiagnosticPhase.Loading)
    val phase: StateFlow<DiagnosticPhase> = mutable.asStateFlow()
    private var generation = 0
    private var active = false
    private var job: Job? = null

    fun load() {
        if (active) return
        active = true
        val token = ++generation
        job =
            scope.launch {
                val result =
                    try {
                        withContext(dispatcher) { source.snapshot() }
                    } catch (cancellation: CancellationException) {
                        active = false
                        throw cancellation
                    } catch (_: Exception) {
                        null
                    }
                active = false
                apply(token, result)
            }
    }

    fun cancel() {
        generation += 1
        active = false
        job?.cancel()
        job = null
    }

    fun dispose() = cancel()

    internal fun apply(
        token: Int,
        result: String?,
    ) {
        if (token != generation) return
        mutable.value =
            if (result == null) {
                DiagnosticPhase.Error("Runtime unavailable")
            } else {
                DiagnosticPhase.Content(result)
            }
    }
}

fun createRuntimeController(source: RuntimeSource): RuntimeController = RuntimeController(source, MainScope())
