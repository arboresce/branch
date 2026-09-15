import BranchUI
import SwiftUI

@main
struct BranchApp: App {
    @StateObject private var store = RuntimeStore()
    var body: some Scene {
        WindowGroup {
            Group {
                if let snapshot = store.snapshot {
                    DiagnosticHost(snapshot: snapshot).ignoresSafeArea()
                } else {
                    ProgressView("Loading runtime…")
                }
            }
            .task { await store.load() }
        }
    }
}

struct DiagnosticHost: UIViewControllerRepresentable {
    let snapshot: String
    func makeUIViewController(context: Context) -> UIViewController {
        MainViewControllerKt.makeDiagnosticViewController(snapshot: snapshot)
    }
    func updateUIViewController(_ controller: UIViewController, context: Context) {}
}
