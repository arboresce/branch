package ai.arboresce.branch.catalog.host

import ai.arboresce.branch.catalog.CatalogRoot
import ai.arboresce.branch.shared.RuntimeController
import androidx.compose.runtime.Composable
import androidx.compose.runtime.DisposableEffect
import androidx.lifecycle.Lifecycle
import androidx.lifecycle.LifecycleEventObserver
import androidx.lifecycle.compose.LocalLifecycleOwner

/** Ties the catalog controller to the hosting lifecycle; disposal stays with its owner. */
@Composable
fun CatalogHost(controller: RuntimeController) {
    val lifecycle = LocalLifecycleOwner.current.lifecycle
    DisposableEffect(lifecycle, controller) {
        val observer =
            LifecycleEventObserver { _, event ->
                when (event) {
                    Lifecycle.Event.ON_START -> controller.load()
                    Lifecycle.Event.ON_STOP -> controller.cancel()
                    else -> Unit
                }
            }
        lifecycle.addObserver(observer)
        if (lifecycle.currentState.isAtLeast(Lifecycle.State.STARTED)) controller.load()
        onDispose { lifecycle.removeObserver(observer) }
    }
    CatalogRoot(controller)
}
