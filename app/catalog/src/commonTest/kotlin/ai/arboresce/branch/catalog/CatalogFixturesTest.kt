package ai.arboresce.branch.catalog

import ai.arboresce.branch.shared.RuntimeController
import ai.arboresce.branch.ui.DiagnosticPhase
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertIs
import kotlin.test.assertTrue

class CatalogFixturesTest {
    @Test
    fun itemsAreDeterministicAndNamespaced() {
        val first = CatalogFixtures.items
        val second = CatalogFixtures.items
        assertEquals(first, second)
        assertEquals(first.map { it.id }, listOf("catalog-item-1", "catalog-item-2", "catalog-item-3", "catalog-item-4", "catalog-item-5"))
        assertTrue(first.all { it.id.startsWith("catalog-") })
    }

    @Test
    fun mediaAndFormAreDeterministic() {
        assertEquals(CatalogFixtures.media, CatalogFixtures.media)
        assertEquals(CatalogFixtures.form, CatalogFixtures.form)
        assertEquals(2, CatalogFixtures.media.size)
        assertEquals(2, CatalogFixtures.form.size)
    }

    @Test
    fun clockIsFixed() {
        assertEquals(CatalogFixtures.FIXED_NOW_MILLIS, FixedCatalogClock().nowMillis())
    }

    @Test
    fun scriptedSourceStepsThroughSuccessiveSnapshots() {
        val source = ScriptedRuntimeSource()
        assertEquals(CatalogFixtures.runtimeSnapshots[0], source.snapshot())
        assertEquals(CatalogFixtures.runtimeSnapshots[1], source.snapshot())
        assertEquals(CatalogFixtures.runtimeSnapshots[1], source.snapshot())
    }

    @Test
    fun catalogConsumesTheSharedControllerWithFixtures() {
        val controller =
            RuntimeController(
                ScriptedRuntimeSource(),
                CoroutineScope(Dispatchers.Unconfined),
                Dispatchers.Unconfined,
            )
        controller.load()
        assertEquals(
            CatalogFixtures.runtimeSnapshots[0],
            assertIs<DiagnosticPhase.Content>(controller.phase.value).text,
        )
        controller.load()
        assertEquals(
            CatalogFixtures.runtimeSnapshots[1],
            assertIs<DiagnosticPhase.Content>(controller.phase.value).text,
        )
    }
}
