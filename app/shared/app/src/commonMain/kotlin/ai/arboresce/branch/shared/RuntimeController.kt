package ai.arboresce.branch.shared

import ai.arboresce.branch.ui.DiagnosticPhase
import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.CoroutineDispatcher
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.Job
import kotlinx.coroutines.MainScope
import kotlinx.coroutines.cancel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock
import kotlinx.coroutines.withContext

class RuntimeController(
    private val source: RuntimeSource,
    private val scope: CoroutineScope,
    private val dispatcher: CoroutineDispatcher = Dispatchers.Default,
    private val ownsScope: Boolean = false,
) {
    private val mutable = MutableStateFlow<DiagnosticPhase>(DiagnosticPhase.Loading)
    val phase: StateFlow<DiagnosticPhase> = mutable.asStateFlow()
    private val nativeCall = Mutex()
    private var generation = 0
    private var active = false
    private var disposed = false
    private var job: Job? = null

    fun load() {
        if (disposed || active) return
        active = true
        val token = ++generation
        mutable.value = DiagnosticPhase.Loading
        job =
            scope.launch {
                val result =
                    try {
                        nativeCall.withLock { withContext(dispatcher) { source.snapshot() } }
                    } catch (cancellation: CancellationException) {
                        settle(token)
                        throw cancellation
                    } catch (_: Exception) {
                        null
                    }
                settle(token)
                publish(token, result)
            }
    }

    fun cancel() {
        generation += 1
        active = false
        job?.cancel()
        job = null
    }

    fun dispose() {
        if (disposed) return
        disposed = true
        cancel()
        if (ownsScope) scope.cancel()
    }

    private fun settle(token: Int) {
        if (token == generation) active = false
    }

    private fun publish(
        token: Int,
        result: String?,
    ) {
        if (disposed || token != generation) return
        mutable.value =
            if (result == null) {
                DiagnosticPhase.Error("Runtime unavailable")
            } else {
                DiagnosticPhase.Content(result)
            }
    }
}

fun createRuntimeController(source: RuntimeSource): RuntimeController {
    val scope = MainScope()
    return RuntimeController(source, scope, ownsScope = true)
}
