import BranchUI
import Foundation

final class RustRuntimeSource: AppRuntimeSource {
    private lazy var runtime = BranchRuntime()

    func snapshot() -> String? {
        try? runtime.snapshotJson()
    }
}

/// App-lifetime owner of the shared controller. Inactive/background cancels; active
/// resumes with one load; a transient view disappearance only cancels. Disposal happens
/// once, when this owner is removed.
@MainActor
final class RuntimeStore: ObservableObject {
    nonisolated(unsafe) let controller: AppRuntimeController =
        MainViewControllerKt.createDiagnosticController(source: RustRuntimeSource())

    func load() {
        controller.load()
    }

    func cancel() {
        controller.cancel()
    }

    func dispose() {
        controller.dispose()
    }

    deinit {
        controller.dispose()
    }
}
