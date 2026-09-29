import BranchUI
import SwiftUI

@main
struct BranchApp: App {
    @StateObject private var store = RuntimeStore()
    @Environment(\.scenePhase) private var scenePhase

    var body: some Scene {
        WindowGroup {
            DiagnosticHost(controller: store.controller)
                .ignoresSafeArea()
                .task { store.load() }
                .onDisappear { store.dispose() }
                .onChange(of: scenePhase) { _, phase in
                    if phase != .active {
                        store.cancel()
                    }
                }
        }
    }
}

struct DiagnosticHost: UIViewControllerRepresentable {
    let controller: AppRuntimeController

    func makeUIViewController(context: Context) -> UIViewController {
        MainViewControllerKt.makeDiagnosticViewController(controller: controller)
    }

    func updateUIViewController(_ controller: UIViewController, context: Context) {}
}
