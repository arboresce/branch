package ai.arboresce.branch.shared

import ai.arboresce.branch.ui.DiagnosticPhase
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.Job
import kotlinx.coroutines.TimeoutCancellationException
import kotlinx.coroutines.cancel
import kotlinx.coroutines.channels.Channel
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.isActive
import kotlinx.coroutines.runBlocking
import kotlinx.coroutines.withTimeout
import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertFailsWith
import kotlin.test.assertFalse
import kotlin.test.assertIs
import kotlin.test.assertTrue
import kotlin.time.Duration
import kotlin.time.Duration.Companion.milliseconds
import kotlin.time.Duration.Companion.seconds
import kotlin.time.TimeSource

/**
 * Controller orchestration is serialized on one controlled executor; only the
 * blocking native fake runs on the separate worker, matching host ownership.
 */
private val CONTROLLER_EXECUTOR = Dispatchers.Default.limitedParallelism(1)
private val NATIVE_WORKER = Dispatchers.Default.limitedParallelism(1)

private val START_BOUND = 5.seconds
private val COMPLETION_BOUND = 5.seconds
private val WORKER_BOUND = 20.seconds
private val SCENARIO_BOUND = 30.seconds

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
        val deadline = TimeSource.Monotonic.markNow()
        while (!gate.value) {
            if (deadline.elapsedNow() > WORKER_BOUND) {
                throw AssertionError("worker was not released within $WORKER_BOUND")
            }
        }
        return result
    }

    suspend fun awaitStart(timeout: Duration = START_BOUND) {
        try {
            withTimeout(timeout) { started.receive() }
        } catch (_: TimeoutCancellationException) {
            throw AssertionError("a source call did not start within $timeout")
        }
    }

    fun hasStarted(): Boolean = started.tryReceive().isSuccess

    fun release() {
        gate.value = true
    }
}

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
    fun pauseWhileBlockedThenResumeDoesNotOverlapOrDuplicate() {
        runBlocking {
            val source = BlockingSource()
            val scope = CoroutineScope(CONTROLLER_EXECUTOR + Job())
            val controller = RuntimeController(source, scope, NATIVE_WORKER)
            try {
                withTimeout(SCENARIO_BOUND) {
                    controller.load()
                    source.awaitStart()
                    controller.cancel()
                    controller.load()
                    assertFalse(
                        source.hasStarted(),
                        "B must not enter while A still holds the native call",
                    )
                    assertEquals(1, source.calls)
                    source.release()
                    source.awaitStart()
                    controller.load()
                    assertFalse(
                        source.hasStarted(),
                        "C while B is active must not start another call",
                    )
                    assertEquals(2, source.calls)
                    source.release()
                    controller.awaitContent("ok")
                    assertEquals(2, source.calls)
                }
            } finally {
                source.release()
                controller.dispose()
                scope.cancel()
                scope.awaitTermination()
            }
        }
    }

    @Test
    fun resumeAfterCancellationLoadsExactlyOnce() {
        runBlocking {
            val source = BlockingSource("resumed")
            val scope = CoroutineScope(CONTROLLER_EXECUTOR + Job())
            val controller = RuntimeController(source, scope, NATIVE_WORKER)
            try {
                withTimeout(SCENARIO_BOUND) {
                    controller.load()
                    source.awaitStart()
                    controller.cancel()
                    source.release()
                    controller.load()
                    source.awaitStart()
                    assertEquals(2, source.calls)
                    source.release()
                    controller.awaitContent("resumed")
                    assertEquals(2, source.calls)
                }
            } finally {
                source.release()
                controller.dispose()
                scope.cancel()
                scope.awaitTermination()
            }
        }
    }

    @Test
    fun disposeWhileBlockedRejectsCompletionAndLaterLoads() {
        runBlocking {
            val source = BlockingSource("late")
            val scope = CoroutineScope(CONTROLLER_EXECUTOR + Job())
            val controller = RuntimeController(source, scope, NATIVE_WORKER)
            try {
                withTimeout(SCENARIO_BOUND) {
                    controller.load()
                    source.awaitStart()
                    controller.dispose()
                    scope.cancel()
                    source.release()
                    controller.load()
                    assertFalse(source.hasStarted())
                    assertEquals(1, source.calls)
                    assertIs<DiagnosticPhase.Loading>(controller.phase.value)
                }
            } finally {
                source.release()
                controller.dispose()
                scope.cancel()
                scope.awaitTermination()
            }
        }
    }

    @Test
    fun missingStartIsDetectedWithinTheBound() {
        runBlocking {
            val source = BlockingSource()
            try {
                val elapsed = TimeSource.Monotonic.markNow()
                assertFailsWith<AssertionError> {
                    source.awaitStart(timeout = 500.milliseconds)
                }
                assertTrue(elapsed.elapsedNow() < 5.seconds)
            } finally {
                source.release()
            }
        }
    }

    @Test
    fun withheldCompletionIsDetectedWithinTheBound() {
        runBlocking {
            val source = BlockingSource("late")
            val scope = CoroutineScope(CONTROLLER_EXECUTOR + Job())
            val controller = RuntimeController(source, scope, NATIVE_WORKER)
            try {
                controller.load()
                source.awaitStart()
                val elapsed = TimeSource.Monotonic.markNow()
                assertFailsWith<AssertionError> {
                    controller.awaitContent("late", timeout = 500.milliseconds)
                }
                assertTrue(elapsed.elapsedNow() < 5.seconds)
                assertEquals(1, source.calls)
            } finally {
                source.release()
                controller.dispose()
                scope.cancel()
                scope.awaitTermination()
            }
        }
    }

    private suspend fun CoroutineScope.awaitTermination() {
        coroutineContext[Job]?.join()
    }

    private suspend fun RuntimeController.awaitContent(
        expected: String,
        timeout: Duration = COMPLETION_BOUND,
    ) {
        val started = TimeSource.Monotonic.markNow()
        while (true) {
            val phase = phase.value
            if (phase is DiagnosticPhase.Content && phase.text == expected) return
            if (started.elapsedNow() > timeout) {
                throw AssertionError("Expected published content: $expected")
            }
            delay(5)
        }
    }
}
