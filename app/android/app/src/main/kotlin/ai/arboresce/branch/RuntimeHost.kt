package ai.arboresce.branch

import ai.arboresce.branch.shared.AppRoot
import ai.arboresce.branch.shared.RuntimeController
import androidx.compose.runtime.Composable
import androidx.compose.runtime.DisposableEffect
import androidx.lifecycle.Lifecycle
import androidx.lifecycle.LifecycleEventObserver
import androidx.lifecycle.compose.LocalLifecycleOwner

@Composable
fun RuntimeHost(controller: RuntimeController) {
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
    AppRoot(controller)
}
