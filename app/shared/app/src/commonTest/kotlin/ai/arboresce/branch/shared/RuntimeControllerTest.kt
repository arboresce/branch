package ai.arboresce.branch.shared

import ai.arboresce.branch.ui.DiagnosticPhase
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.Job
import kotlinx.coroutines.cancel
import kotlinx.coroutines.isActive
import kotlin.test.Test
import kotlin.test.assertEquals
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
    fun cancelledGenerationDoesNotClearNewerActiveState() {
        lateinit var controller: RuntimeController
        var calls = 0
        val source =
            object : RuntimeSource {
                override fun snapshot(): String? {
                    calls += 1
                    if (calls == 1) {
                        controller.cancel()
                        controller.load()
                        return "old"
                    }
                    return "new"
                }
            }
        controller = controllerFor(source)
        controller.load()
        assertEquals("new", assertIs<DiagnosticPhase.Content>(controller.phase.value).text)
        assertEquals(2, calls)
    }

    @Test
    fun staleCompletionDoesNotReplaceCurrentPhase() {
        lateinit var controller: RuntimeController
        var calls = 0
        val source =
            object : RuntimeSource {
                override fun snapshot(): String? {
                    calls += 1
                    if (calls == 1) {
                        controller.cancel()
                        controller.load()
                        return "stale"
                    }
                    return "current"
                }
            }
        controller = controllerFor(source)
        controller.load()
        assertEquals("current", assertIs<DiagnosticPhase.Content>(controller.phase.value).text)
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
}
