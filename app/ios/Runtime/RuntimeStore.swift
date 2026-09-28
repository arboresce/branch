import BranchUI
import Foundation

final class RustRuntimeSource: AppRuntimeSource {
    private lazy var runtime = BranchRuntime()

    func snapshot() -> String? {
        try? runtime.snapshotJson()
    }
}

@MainActor
final class RuntimeStore: ObservableObject {
    let controller: AppRuntimeController =
        MainViewControllerKt.createDiagnosticController(source: RustRuntimeSource())

    func load() {
        controller.load()
    }
}
