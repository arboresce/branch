package ai.arboresce.branch.catalog

import androidx.navigation3.runtime.NavBackStack
import androidx.navigation3.runtime.NavKey
import androidx.navigation3.runtime.serialization.NavBackStackSerializer
import kotlinx.serialization.PolymorphicSerializer
import kotlinx.serialization.json.Json
import kotlinx.serialization.modules.SerializersModule
import kotlinx.serialization.modules.polymorphic
import kotlinx.serialization.modules.subclass
import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertFalse
import kotlin.test.assertTrue

private val probeJson =
    Json {
        serializersModule =
            SerializersModule {
                polymorphic(NavKey::class) {
                    subclass(CatalogHome::class)
                    subclass(CatalogDetail::class)
                }
            }
    }

class CatalogProbesTest {
    @Test
    fun navigationRoutesRoundTripThroughSerialization() {
        val stack = NavBackStack<NavKey>(CatalogHome, CatalogDetail("catalog-item-1"))
        val serializer = NavBackStackSerializer(PolymorphicSerializer(NavKey::class))
        val encoded = probeJson.encodeToString(serializer, stack)
        val restored = probeJson.decodeFromString(serializer, encoded)
        assertEquals(
            listOf<NavKey>(CatalogHome, CatalogDetail("catalog-item-1")),
            restored.toList(),
        )
    }

    @Test
    fun glassFallbackIsSelectedWhenEffectsAreDisabled() {
        assertFalse(glassEffectsAvailable(effectsEnabled = false))
    }

    @Test
    fun glassFallbackIsSelectedWhenCapabilityIsUnavailable() {
        assertFalse(glassEffectsAvailable(effectsEnabled = true, capabilityAvailable = false))
        assertTrue(glassEffectsAvailable(effectsEnabled = true, capabilityAvailable = true))
    }

    @Test
    fun deterministicImageFixtureIsANonEmptyPng() {
        assertTrue(CatalogFixtures.probeImageBytes.size > 8)
        assertEquals(0x89, CatalogFixtures.probeImageBytes[0].toInt() and 0xff)
        assertEquals(0x50, CatalogFixtures.probeImageBytes[1].toInt() and 0xff)
    }
}
