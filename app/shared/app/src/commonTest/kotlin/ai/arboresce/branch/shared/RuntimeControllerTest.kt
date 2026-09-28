package ai.arboresce.branch.shared

import ai.arboresce.branch.ui.DiagnosticPhase
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
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
    fun staleCompletionDoesNotReplaceCurrentPhase() {
        val controller = controllerFor(FakeSource("current"))
        controller.load()
        controller.apply(0, "stale")
        assertEquals("current", assertIs<DiagnosticPhase.Content>(controller.phase.value).text)
    }

    @Test
    fun cancelSuppressesLateCompletion() {
        val controller = controllerFor(FakeSource("first"))
        controller.load()
        val settled = controller.phase.value
        controller.cancel()
        controller.apply(1, "late")
        assertEquals(settled, controller.phase.value)
    }

    @Test
    fun cancelBeforeAnyResultIsNotAFailure() {
        val controller = controllerFor(FakeSource())
        controller.cancel()
        assertIs<DiagnosticPhase.Loading>(controller.phase.value)
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
}
