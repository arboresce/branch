package ai.arboresce.branch.shared

import ai.arboresce.branch.ui.DiagnosticPhase
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.ExperimentalCoroutinesApi
import kotlinx.coroutines.Job
import kotlinx.coroutines.cancel
import kotlinx.coroutines.channels.Channel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.isActive
import kotlinx.coroutines.test.runCurrent
import kotlinx.coroutines.test.runTest
import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertFalse
import kotlin.test.assertIs
import kotlin.test.assertTrue

private class FakeSource(
    var text: String? = "first",
) : RuntimeSource {
    var calls = 0

    override fun snapshot(): String? {
        calls += 1
        return text
    }
}

private fun controllerFor(source: RuntimeSource): RuntimeController =
    RuntimeController(source, CoroutineScope(Dispatchers.Unconfined), Dispatchers.Unconfined)

/**
 * A source whose [snapshot] blocks on a worker thread until the test releases it. The
 * gate uses a [MutableStateFlow] so the test thread and worker thread share state
 * without an unmodelled data race.
 */
private class BlockingSource(
    private val result: String? = "ok",
) : RuntimeSource {
    private val started = Channel<Unit>(Channel.UNLIMITED)
    private val gate = MutableStateFlow(false)
    private val callCount = MutableStateFlow(0)

    val calls: Int get() = callCount.value

    override fun snapshot(): String? {
        callCount.value += 1
        gate.value = false
        started.trySend(Unit)
        while (!gate.value) {
            // Block until the test releases this call.
        }
        return result
    }

    suspend fun awaitStart() {
        started.receive()
    }

    fun hasStarted(): Boolean = started.tryReceive().isSuccess

    fun release() {
        gate.value = true
    }
}

@OptIn(ExperimentalCoroutinesApi::class)
class RuntimeControllerTest {
    @Test
    fun reportsLoadingBeforeAnyResult() {
        assertIs<DiagnosticPhase.Loading>(controllerFor(FakeSource()).phase.value)
    }

    @Test
    fun successiveUpdatesReachTheSameController() {
        val source = FakeSource("first")
        val controller = controllerFor(source)
        controller.load()
        assertEquals("first", assertIs<DiagnosticPhase.Content>(controller.phase.value).text)
        source.text = "second"
        controller.load()
        assertEquals("second", assertIs<DiagnosticPhase.Content>(controller.phase.value).text)
        assertEquals(2, source.calls)
    }

    @Test
    fun unavailableRuntimeProducesSanitizedError() {
        val controller = controllerFor(FakeSource(null))
        controller.load()
        val error = assertIs<DiagnosticPhase.Error>(controller.phase.value)
        assertEquals("Runtime unavailable", error.message)
        assertTrue(!error.message.contains("secret"))
    }

    @Test
    fun thrownRuntimeFailureIsSanitized() {
        val controller =
            controllerFor(
                object : RuntimeSource {
                    override fun snapshot(): String? = throw IllegalStateException("secret detail")
                },
            )
        controller.load()
        assertEquals(
            "Runtime unavailable",
            assertIs<DiagnosticPhase.Error>(controller.phase.value).message,
        )
    }

    @Test
    fun cancelBeforeAnyResultIsNotAFailure() {
        val controller = controllerFor(FakeSource())
        controller.cancel()
        assertIs<DiagnosticPhase.Loading>(controller.phase.value)
    }

    @Test
    fun cancelPermitsAnExplicitReload() {
        val source = FakeSource("first")
        val controller = controllerFor(source)
        controller.load()
        controller.cancel()
        source.text = "second"
        controller.load()
        assertEquals("second", assertIs<DiagnosticPhase.Content>(controller.phase.value).text)
    }

    @Test
    fun duplicateLoadWhileActiveIsIgnored() {
        lateinit var controller: RuntimeController
        val source =
            object : RuntimeSource {
                var calls = 0

                override fun snapshot(): String? {
                    calls += 1
                    controller.load()
                    return "once"
                }
            }
        controller = controllerFor(source)
        controller.load()
        assertEquals(1, source.calls)
        assertEquals("once", assertIs<DiagnosticPhase.Content>(controller.phase.value).text)
    }

    @Test
    fun retryFromErrorEntersLoadingBeforeContent() {
        lateinit var controller: RuntimeController
        var calls = 0
        var sawLoadingOnRetry = false
        val source =
            object : RuntimeSource {
                override fun snapshot(): String? {
                    calls += 1
                    if (calls == 1) return null
                    sawLoadingOnRetry = controller.phase.value is DiagnosticPhase.Loading
                    return "recovered"
                }
            }
        controller = controllerFor(source)
        controller.load()
        assertIs<DiagnosticPhase.Error>(controller.phase.value)
        controller.load()
        assertTrue(sawLoadingOnRetry)
        assertEquals("recovered", assertIs<DiagnosticPhase.Content>(controller.phase.value).text)
    }

    @Test
    fun disposalIsTerminalAndRejectsLaterLoads() {
        val source = FakeSource("first")
        val controller = controllerFor(source)
        controller.load()
        controller.dispose()
        controller.load()
        assertEquals(1, source.calls)
        assertEquals("first", assertIs<DiagnosticPhase.Content>(controller.phase.value).text)
    }

    @Test
    fun disposeCancelsAnOwnedScope() {
        val scope = CoroutineScope(Dispatchers.Unconfined + Job())
        val controller =
            RuntimeController(FakeSource(), scope, Dispatchers.Unconfined, ownsScope = true)
        controller.dispose()
        assertTrue(!scope.isActive)
    }

    @Test
    fun disposeKeepsAnExternallyOwnedScope() {
        val scope = CoroutineScope(Dispatchers.Unconfined + Job())
        val controller =
            RuntimeController(FakeSource(), scope, Dispatchers.Unconfined, ownsScope = false)
        controller.dispose()
        assertTrue(scope.isActive)
        scope.cancel()
    }

    @Test
    fun pauseWhileBlockedThenResumeDoesNotOverlapOrDuplicate() =
        runTest {
            val source = BlockingSource()
            val controller = RuntimeController(source, backgroundScope, Dispatchers.Default)
            controller.load()
            runCurrent()
            source.awaitStart()
            controller.cancel()
            controller.load()
            runCurrent()
            assertFalse(source.hasStarted(), "B must not enter while A still holds the native call")
            assertEquals(1, source.calls)
            source.release()
            source.awaitStart()
            controller.load()
            runCurrent()
            assertFalse(source.hasStarted(), "C while B is active must not start another call")
            assertEquals(2, source.calls)
            source.release()
            runCurrent()
            assertEquals(2, source.calls)
            controller.dispose()
        }

    @Test
    fun resumeAfterCancellationLoadsExactlyOnce() =
        runTest {
            val source = BlockingSource("resumed")
            val controller = RuntimeController(source, backgroundScope, Dispatchers.Default)
            controller.load()
            runCurrent()
            source.awaitStart()
            controller.cancel()
            source.release()
            runCurrent()
            controller.load()
            runCurrent()
            source.awaitStart()
            assertEquals(2, source.calls)
            source.release()
            runCurrent()
            assertEquals(2, source.calls)
            controller.dispose()
        }

    @Test
    fun disposeWhileBlockedRejectsCompletionAndLaterLoads() =
        runTest {
            val source = BlockingSource("late")
            val controller = RuntimeController(source, backgroundScope, Dispatchers.Default)
            controller.load()
            runCurrent()
            source.awaitStart()
            controller.dispose()
            source.release()
            runCurrent()
            controller.load()
            runCurrent()
            assertFalse(source.hasStarted())
            assertEquals(1, source.calls)
            assertIs<DiagnosticPhase.Loading>(controller.phase.value)
        }
}
