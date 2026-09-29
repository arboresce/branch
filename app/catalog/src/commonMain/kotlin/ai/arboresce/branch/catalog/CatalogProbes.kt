package ai.arboresce.branch.catalog

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
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

fun glassEffectsAvailable(
    effectsEnabled: Boolean,
    capabilityAvailable: Boolean = true,
): Boolean = effectsEnabled && capabilityAvailable

@Composable
fun CatalogGlassProbe(
    effectsEnabled: Boolean = true,
    capabilityAvailable: Boolean = true,
) {
    if (!glassEffectsAvailable(effectsEnabled, capabilityAvailable)) {
        Box(
            Modifier
                .fillMaxWidth()
                .height(64.dp)
                .background(Color(0xFF22242A))
                .testTag("glass-fallback"),
        ) {
            BasicText("Opaque glass fallback", Modifier.padding(12.dp))
        }
        return
    }
    val backdrop = rememberLayerBackdrop()
    Box(Modifier.fillMaxWidth().height(64.dp).testTag("glass-surface")) {
        Box(
            Modifier
                .matchParentSize()
                .layerBackdrop(backdrop)
                .background(Color(0xFF3150A0)),
        )
        Box(
            Modifier
                .matchParentSize()
                .drawBackdrop(
                    backdrop = backdrop,
                    shape = { RoundedCornerShape(12.dp) },
                    effects = { blur(8f) },
                ),
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

@Composable
fun CatalogProbes() {
    Column {
        CatalogNavigationProbe()
        CatalogGlassProbe()
        CatalogImageProbe()
    }
}
