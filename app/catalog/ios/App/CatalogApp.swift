import BranchCatalogUI
import SwiftUI

@main
struct CatalogApp: App {
    var body: some Scene {
        WindowGroup {
            CatalogHost().ignoresSafeArea()
        }
    }
}

struct CatalogHost: UIViewControllerRepresentable {
    func makeUIViewController(context: Context) -> UIViewController {
        CatalogBridgeKt.makeCatalogViewController()
    }

    func updateUIViewController(_ controller: UIViewController, context: Context) {}
}
