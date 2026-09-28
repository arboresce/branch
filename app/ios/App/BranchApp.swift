import BranchUI
import SwiftUI

@main
struct BranchApp: App {
    @StateObject private var store = RuntimeStore()

    var body: some Scene {
        WindowGroup {
            DiagnosticHost(controller: store.controller)
                .ignoresSafeArea()
                .task { store.load() }
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
