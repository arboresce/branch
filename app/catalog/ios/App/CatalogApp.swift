import BranchCatalogUI
import SwiftUI

@MainActor
final class CatalogStore: ObservableObject {
    nonisolated(unsafe) let controller: AppRuntimeController =
        CatalogBridgeKt.createCatalogController()

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

@main
struct CatalogApp: App {
    @StateObject private var store = CatalogStore()
    @Environment(\.scenePhase) private var scenePhase

    var body: some Scene {
        WindowGroup {
            CatalogHost(controller: store.controller)
                .ignoresSafeArea()
                .task { store.load() }
                .onDisappear { store.cancel() }
                .onChange(of: scenePhase) { _, phase in
                    if phase == .active {
                        store.load()
                    } else {
                        store.cancel()
                    }
                }
        }
    }
}

struct CatalogHost: UIViewControllerRepresentable {
    let controller: AppRuntimeController

    func makeUIViewController(context: Context) -> UIViewController {
        CatalogBridgeKt.makeCatalogViewController(controller: controller)
    }

    func updateUIViewController(_ controller: UIViewController, context: Context) {}
}
