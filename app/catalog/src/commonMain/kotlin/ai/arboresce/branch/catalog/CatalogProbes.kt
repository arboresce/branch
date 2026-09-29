package ai.arboresce.branch.catalog

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxHeight
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.BasicText
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.ColorProducer
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.unit.dp
import androidx.navigation3.runtime.NavEntry
import androidx.navigation3.runtime.NavKey
import androidx.navigation3.runtime.rememberNavBackStack
import androidx.navigation3.ui.NavDisplay
import androidx.savedstate.serialization.SavedStateConfiguration
import coil3.compose.AsyncImage
import com.kyant.backdrop.backdrops.layerBackdrop
import com.kyant.backdrop.backdrops.rememberLayerBackdrop
import com.kyant.backdrop.drawBackdrop
import com.kyant.backdrop.effects.blur
import kotlinx.serialization.Serializable
import kotlinx.serialization.modules.SerializersModule
import kotlinx.serialization.modules.polymorphic
import kotlinx.serialization.modules.subclass

@Serializable
data object CatalogHome : NavKey

@Serializable
data class CatalogDetail(
    val id: String,
) : NavKey

val catalogNavigationConfiguration: SavedStateConfiguration =
    SavedStateConfiguration {
        serializersModule =
            SerializersModule {
                polymorphic(NavKey::class) {
                    subclass(CatalogHome::class)
                    subclass(CatalogDetail::class)
                }
            }
    }

@Composable
fun CatalogNavigationProbe() {
    val backStack = rememberNavBackStack(catalogNavigationConfiguration, CatalogHome)
    Box(Modifier.fillMaxWidth().height(120.dp).testTag("nav3-probe")) {
        NavDisplay(
            backStack = backStack,
            onBack = { if (backStack.size > 1) backStack.removeAt(backStack.lastIndex) },
            entryProvider = { key ->
                when (key) {
                    is CatalogHome ->
                        NavEntry(key) {
                            Column(Modifier.testTag("nav3-home")) {
                                BasicText("Home entry")
                                BasicText(
                                    "Open detail",
                                    Modifier
                                        .testTag("nav3-push")
                                        .clickable {
                                            backStack.add(CatalogDetail(CatalogFixtures.items.first().id))
                                        },
                                )
                            }
                        }

                    is CatalogDetail ->
                        NavEntry(key) {
                            Column(Modifier.testTag("nav3-detail")) {
                                BasicText("Detail ${key.id}")
                                BasicText(
                                    "Back",
                                    Modifier
                                        .testTag("nav3-pop")
                                        .clickable { backStack.removeAt(backStack.lastIndex) },
                                )
                            }
                        }

                    else -> NavEntry(key) { BasicText("Unknown entry") }
                }
            },
        )
    }
}

const val GLASS_MIN_BLUR_API: Int = 31

const val GLASS_FALLBACK_BACKGROUND: Long = 0xFF22242A
const val GLASS_FALLBACK_FOREGROUND: Long = 0xFFF5F5F5

fun glassCapabilityAvailable(sdkInt: Int): Boolean = sdkInt >= GLASS_MIN_BLUR_API

fun glassEffectsAvailable(
    effectsEnabled: Boolean,
    capabilityAvailable: Boolean,
): Boolean = effectsEnabled && capabilityAvailable

@Composable
fun CatalogGlassProbe(
    effectsEnabled: Boolean,
    hostCapabilityAvailable: Boolean,
    tag: String,
) {
    if (!glassEffectsAvailable(effectsEnabled, hostCapabilityAvailable)) {
        Box(
            Modifier
                .fillMaxWidth()
                .height(64.dp)
                .background(Color(GLASS_FALLBACK_BACKGROUND))
                .testTag("$tag-box"),
        ) {
            BasicText(
                "Opaque glass fallback",
                color = ColorProducer { Color(GLASS_FALLBACK_FOREGROUND) },
                modifier = Modifier.padding(12.dp).testTag(tag),
            )
        }
        return
    }
    val backdrop = rememberLayerBackdrop()
    Box(Modifier.fillMaxWidth().height(64.dp).testTag("$tag-box")) {
        PatternedSource(Modifier.matchParentSize().layerBackdrop(backdrop))
        Box(
            Modifier
                .matchParentSize()
                .drawBackdrop(
                    backdrop = backdrop,
                    shape = { RoundedCornerShape(12.dp) },
                    effects = { blur(8f) },
                ),
        )
        BasicText(
            "Live glass surface",
            Modifier.padding(12.dp).testTag(tag),
        )
    }
}

@Composable
private fun PatternedSource(modifier: Modifier) {
    Row(modifier) {
        listOf(
            Color(0xFFD32F2F),
            Color(0xFF388E3C),
            Color(0xFF1976D2),
            Color(0xFFFFC107),
        ).forEach { color ->
            Box(Modifier.weight(1f).fillMaxHeight().background(color))
        }
    }
}

@Composable
fun CatalogGlassGallery(hostCapabilityAvailable: Boolean) {
    Column {
        CatalogGlassProbe(
            effectsEnabled = true,
            hostCapabilityAvailable = hostCapabilityAvailable,
            tag = "glass-surface",
        )
        CatalogGlassProbe(
            effectsEnabled = true,
            hostCapabilityAvailable = false,
            tag = "glass-fallback-capability",
        )
        CatalogGlassProbe(
            effectsEnabled = false,
            hostCapabilityAvailable = hostCapabilityAvailable,
            tag = "glass-fallback-effects",
        )
    }
}

@Composable
fun CatalogImageProbe() {
    var succeeded by remember { mutableStateOf(false) }
    var failed by remember { mutableStateOf(false) }
    Column {
        Box(Modifier.size(32.dp)) {
            AsyncImage(
                model = CatalogFixtures.probeImageBytes,
                contentDescription = "Deterministic catalog image",
                onSuccess = { succeeded = true },
                onError = { failed = true },
                modifier = Modifier.size(32.dp).testTag("image-probe"),
            )
        }
        Box(Modifier.size(32.dp)) {
            AsyncImage(
                model = "catalog-missing://probe",
                contentDescription = "Missing catalog image",
                onError = { failed = true },
                modifier = Modifier.size(32.dp).testTag("image-missing"),
            )
        }
        if (succeeded) BasicText("image-success", Modifier.testTag("image-success"))
        if (failed) BasicText("image-error", Modifier.testTag("image-error"))
    }
}
