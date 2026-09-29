import BranchCatalogUI
import XCTest

@testable import BranchCatalog

/// Development-only source that publishes distinct revisions and blocks every
/// native call after the first so owner lifetime is observable, not inferred.
private final class ControlledCatalogSource: AppRuntimeSource {
    private let lock = NSLock()
    private var count = 0
    private let gate = DispatchSemaphore(value: 0)

    var calls: Int {
        lock.lock()
        defer { lock.unlock() }
        return count
    }

    func snapshot() -> String? {
        lock.lock()
        count += 1
        let revision = count - 1
        lock.unlock()
        if revision >= 1 {
            _ = gate.wait(timeout: .now() + 30)
        }
        return "revision-\(revision)"
    }

    func release() {
        gate.signal()
    }
}

@MainActor
final class CatalogOwnerTests: XCTestCase {
    private func waitFor(
        _ condition: @escaping () -> Bool,
        timeout: TimeInterval = 5
    ) {
        let deadline = Date().addingTimeInterval(timeout)
        while Date() < deadline, !condition() {
            RunLoop.current.run(until: Date().addingTimeInterval(0.02))
        }
        XCTAssertTrue(condition(), "condition not met within \(timeout)s")
    }

    private func pump(_ interval: TimeInterval = 0.3) {
        RunLoop.current.run(until: Date().addingTimeInterval(interval))
    }

    func testOwnerRemovalDisposesTheControllerAndRejectsLaterLoads() {
        let source = ControlledCatalogSource()
        var store: CatalogStore? = CatalogStore(
            controller: CatalogBridgeKt.createCatalogController(source: source))
        let controller = store!.controller
        defer { source.release() }

        controller.load()
        waitFor { CatalogBridgeKt.catalogPhaseText(controller: controller) == "revision-0" }

        // Hold a second native call in flight, then remove the owning store.
        controller.load()
        waitFor { source.calls == 2 }
        store = nil
        source.release()

        // A disposed owner must suppress the stale completion and publish nothing new.
        pump()
        XCTAssertNotEqual(
            CatalogBridgeKt.catalogPhaseText(controller: controller), "revision-1")
        XCTAssertEqual(CatalogBridgeKt.catalogPhaseKind(controller: controller), "loading")

        // Later loads must be rejected without another source invocation.
        controller.load()
        pump()
        XCTAssertEqual(source.calls, 2)
    }
}
