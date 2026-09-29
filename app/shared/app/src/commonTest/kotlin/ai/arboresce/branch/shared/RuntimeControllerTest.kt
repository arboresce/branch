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
import kotlin.coroutines.ContinuationInterceptor
import kotlin.coroutines.coroutineContext
import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertFailsWith
import kotlin.test.assertFalse
import kotlin.test.assertIs
import kotlin.test.assertSame
import kotlin.test.assertTrue
import kotlin.time.Duration
import kotlin.time.Duration.Companion.milliseconds
import kotlin.time.Duration.Companion.seconds
import kotlin.time.TimeSource

private val CONTROLLER_EXECUTOR = Dispatchers.Default.limitedParallelism(1)
private val NATIVE_WORKER = Dispatchers.Default.limitedParallelism(1)

private val START_BOUND = 5.seconds
private val COMPLETION_BOUND = 5.seconds
private val WORKER_BOUND = 20.seconds
private val SCENARIO_BOUND = 30.seconds
private val CLEANUP_BOUND = 25.seconds
private val SETTLE_BOUND = 5.seconds

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
    private val finishedCount = MutableStateFlow(0)

    val calls: Int get() = callCount.value
    val finished: Int get() = finishedCount.value

    override fun snapshot(): String? {
        callCount.value += 1
        gate.value = false
        started.trySend(Unit)
        try {
            val deadline = TimeSource.Monotonic.markNow()
            while (!gate.value) {
                if (deadline.elapsedNow() > WORKER_BOUND) {
                    throw AssertionError("worker was not released within $WORKER_BOUND")
                }
            }
            return result
        } finally {
            finishedCount.value += 1
        }
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

private fun ownedScope(): CoroutineScope = CoroutineScope(CONTROLLER_EXECUTOR + Job())

private suspend fun assertControllerExecutor() {
    assertSame(CONTROLLER_EXECUTOR, coroutineContext[ContinuationInterceptor])
}

private suspend fun CoroutineScope.awaitTermination(bound: Duration = CLEANUP_BOUND) {
    val job = coroutineContext[Job] ?: return
    withTimeout(bound) { job.join() }
}

private suspend fun CoroutineScope.awaitSettled(bound: Duration = SETTLE_BOUND) {
    val parent = coroutineContext[Job] ?: return
    withTimeout(bound) {
        while (parent.children.any { !it.isCompleted }) {
            parent.children
                .filter { !it.isCompleted }
                .toList()
                .forEach { it.join() }
        }
    }
}

private suspend fun cleanupOwned(
    source: BlockingSource,
    controller: RuntimeController,
    scope: CoroutineScope,
) {
    source.release()
    controller.dispose()
    scope.cancel()
    scope.awaitTermination()
}

private suspend fun runBoundedScenario(
    cleanupBound: Duration = CLEANUP_BOUND,
    cleanup: suspend () -> Unit,
    body: suspend () -> Unit,
) {
    var primary: Throwable? = null
    try {
        withTimeout(SCENARIO_BOUND) { body() }
    } catch (error: Throwable) {
        primary = error
        throw error
    } finally {
        var cleanupFailure: Throwable? = null
        try {
            withTimeout(cleanupBound) { cleanup() }
        } catch (error: Throwable) {
            cleanupFailure = error
        }
        if (cleanupFailure != null) {
            if (primary == null) throw cleanupFailure
            println("cleanup failed after primary failure: $cleanupFailure")
        }
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
    fun pauseWhileBlockedThenResumeDoesNotOverlapOrDuplicate() =
        runBlocking(CONTROLLER_EXECUTOR) {
            val source = BlockingSource()
            val scope = ownedScope()
            val controller = RuntimeController(source, scope, NATIVE_WORKER)
            val elapsed = TimeSource.Monotonic.markNow()
            runBoundedScenario(cleanup = { cleanupOwned(source, controller, scope) }) {
                assertControllerExecutor()
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
            assertTrue(elapsed.elapsedNow() < SCENARIO_BOUND)
            assertEquals(source.calls, source.finished)
        }

    @Test
    fun resumeAfterCancellationLoadsExactlyOnce() =
        runBlocking(CONTROLLER_EXECUTOR) {
            val source = BlockingSource("resumed")
            val scope = ownedScope()
            val controller = RuntimeController(source, scope, NATIVE_WORKER)
            val elapsed = TimeSource.Monotonic.markNow()
            runBoundedScenario(cleanup = { cleanupOwned(source, controller, scope) }) {
                assertControllerExecutor()
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
            assertTrue(elapsed.elapsedNow() < SCENARIO_BOUND)
            assertEquals(source.calls, source.finished)
        }

    @Test
    fun disposeWhileBlockedRejectsCompletionAndLaterLoads() =
        runBlocking(CONTROLLER_EXECUTOR) {
            val source = BlockingSource("late")
            val scope = ownedScope()
            val controller = RuntimeController(source, scope, NATIVE_WORKER)
            val elapsed = TimeSource.Monotonic.markNow()
            runBoundedScenario(cleanup = { cleanupOwned(source, controller, scope) }) {
                assertControllerExecutor()
                controller.load()
                source.awaitStart()
                controller.dispose()
                source.release()
                scope.awaitSettled()
                assertIs<DiagnosticPhase.Loading>(controller.phase.value)
                assertEquals(1, source.calls)
                assertFalse(source.hasStarted())

                controller.load()
                scope.awaitSettled()
                assertIs<DiagnosticPhase.Loading>(controller.phase.value)
                assertEquals(1, source.calls)
                assertFalse(source.hasStarted())
            }
            assertTrue(elapsed.elapsedNow() < SCENARIO_BOUND)
            assertEquals(source.calls, source.finished)
        }

    @Test
    fun missingStartIsDetectedWithinTheBound() =
        runBlocking(CONTROLLER_EXECUTOR) {
            val source = BlockingSource()
            val elapsed = TimeSource.Monotonic.markNow()
            try {
                val failure =
                    assertFailsWith<AssertionError> {
                        withTimeout(SCENARIO_BOUND) {
                            source.awaitStart(timeout = 500.milliseconds)
                        }
                    }
                assertTrue(failure.message.orEmpty().contains("did not start"))
            } finally {
                source.release()
            }
            assertTrue(elapsed.elapsedNow() < SCENARIO_BOUND)
            assertEquals(source.calls, source.finished)
        }

    @Test
    fun withheldCompletionIsDetectedWithinTheBound() =
        runBlocking(CONTROLLER_EXECUTOR) {
            val source = BlockingSource("late")
            val scope = ownedScope()
            val controller = RuntimeController(source, scope, NATIVE_WORKER)
            val elapsed = TimeSource.Monotonic.markNow()
            val failure =
                assertFailsWith<AssertionError> {
                    runBoundedScenario(cleanup = { cleanupOwned(source, controller, scope) }) {
                        assertControllerExecutor()
                        controller.load()
                        source.awaitStart()
                        controller.awaitContent("late", timeout = 500.milliseconds)
                    }
                }
            assertEquals("Expected published content: late", failure.message)
            assertTrue(elapsed.elapsedNow() < SCENARIO_BOUND)
            assertEquals(1, source.calls)
            assertEquals(source.calls, source.finished)
        }

    @Test
    fun cleanupDeadlineIsBoundedAndPreservesPrimaryFailure() =
        runBlocking(CONTROLLER_EXECUTOR) {
            val source = BlockingSource()
            val scope = ownedScope()
            val controller = RuntimeController(source, scope, NATIVE_WORKER)
            val elapsed = TimeSource.Monotonic.markNow()
            val failure =
                assertFailsWith<AssertionError> {
                    runBoundedScenario(
                        cleanupBound = 300.milliseconds,
                        cleanup = {
                            controller.dispose()
                            scope.cancel()
                            scope.awaitTermination()
                        },
                    ) {
                        assertControllerExecutor()
                        controller.load()
                        source.awaitStart()
                        throw AssertionError("primary scenario failure")
                    }
                }
            assertEquals("primary scenario failure", failure.message)
            assertTrue(elapsed.elapsedNow() < SCENARIO_BOUND)
            source.release()
            scope.awaitTermination()
            assertTrue(scope.coroutineContext[Job]?.isCompleted == true)
            assertEquals(1, source.calls)
            assertEquals(source.calls, source.finished)
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
