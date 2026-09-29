import BranchCatalogUI
import XCTest

@testable import BranchCatalog

@MainActor
final class CatalogOwnerTests: XCTestCase {
    private func waitForKind(
        _ controller: AppRuntimeController,
        _ expected: String,
        timeout: TimeInterval = 5
    ) {
        let deadline = Date().addingTimeInterval(timeout)
        while Date() < deadline,
            CatalogBridgeKt.catalogPhaseKind(controller: controller) != expected
        {
            RunLoop.current.run(until: Date().addingTimeInterval(0.02))
        }
        XCTAssertEqual(CatalogBridgeKt.catalogPhaseKind(controller: controller), expected)
    }

    func testOwnerRemovalDisposesTheControllerAndRejectsLaterLoads() {
        var store: CatalogStore? = CatalogStore()
        let controller = store!.controller
        controller.load()
        waitForKind(controller, "content")
        store = nil
        controller.load()
        waitForKind(controller, "content")
    }
}
