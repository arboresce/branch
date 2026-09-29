package ai.arboresce.branch.catalog

import androidx.navigation3.runtime.NavBackStack
import androidx.navigation3.runtime.NavKey
import androidx.navigation3.runtime.serialization.NavBackStackSerializer
import kotlinx.serialization.PolymorphicSerializer
import kotlinx.serialization.json.Json
import kotlinx.serialization.modules.SerializersModule
import kotlinx.serialization.modules.polymorphic
import kotlinx.serialization.modules.subclass
import kotlin.math.pow
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
        assertFalse(glassEffectsAvailable(effectsEnabled = false, capabilityAvailable = true))
    }

    @Test
    fun glassFallbackIsSelectedWhenCapabilityIsUnavailable() {
        assertFalse(glassEffectsAvailable(effectsEnabled = true, capabilityAvailable = false))
        assertTrue(glassEffectsAvailable(effectsEnabled = true, capabilityAvailable = true))
    }

    @Test
    fun api28SelectsTheOpaqueFallback() {
        assertFalse(glassCapabilityAvailable(28))
        assertFalse(
            glassEffectsAvailable(
                effectsEnabled = true,
                capabilityAvailable = glassCapabilityAvailable(28),
            ),
        )
    }

    @Test
    fun api31AndNewerAllowTheLiveSurface() {
        assertTrue(glassCapabilityAvailable(31))
        assertTrue(glassCapabilityAvailable(36))
    }

    @Test
    fun deterministicImageFixtureIsANonEmptyPng() {
        assertTrue(CatalogFixtures.probeImageBytes.size > 8)
        assertEquals(0x89, CatalogFixtures.probeImageBytes[0].toInt() and 0xff)
        assertEquals(0x50, CatalogFixtures.probeImageBytes[1].toInt() and 0xff)
    }

    @Test
    fun fallbackForegroundMeetsMinimumContrast() {
        assertTrue(contrastRatio(GLASS_FALLBACK_FOREGROUND, GLASS_FALLBACK_BACKGROUND) >= 4.5)
    }

    private fun luminance(argb: Long): Double {
        fun channel(shift: Int): Double {
            val value = ((argb shr shift) and 0xFF).toDouble() / 255.0
            return if (value <= 0.03928) value / 12.92 else ((value + 0.055) / 1.055).pow(2.4)
        }
        return 0.2126 * channel(16) + 0.7152 * channel(8) + 0.0722 * channel(0)
    }

    private fun contrastRatio(
        foreground: Long,
        background: Long,
    ): Double {
        val a = luminance(foreground)
        val b = luminance(background)
        return (maxOf(a, b) + 0.05) / (minOf(a, b) + 0.05)
    }
}
