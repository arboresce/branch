import BranchUI
import XCTest

private final class FakeRuntimeSource: AppRuntimeSource {
    var value: String? = "first"

    func snapshot() -> String? {
        value
    }
}

final class RuntimeControllerTests: XCTestCase {
    private func waitForKind(
        _ controller: AppRuntimeController,
        _ expected: String
    ) {
        let deadline = Date().addingTimeInterval(5)
        while Date() < deadline,
            MainViewControllerKt.diagnosticPhaseKind(controller: controller) != expected
        {
            RunLoop.current.run(until: Date().addingTimeInterval(0.02))
        }
        XCTAssertEqual(MainViewControllerKt.diagnosticPhaseKind(controller: controller), expected)
    }

    private func waitForContent(
        _ controller: AppRuntimeController,
        _ expected: String
    ) {
        let deadline = Date().addingTimeInterval(5)
        while Date() < deadline,
            MainViewControllerKt.diagnosticContent(controller: controller) != expected
        {
            RunLoop.current.run(until: Date().addingTimeInterval(0.02))
        }
        XCTAssertEqual(MainViewControllerKt.diagnosticContent(controller: controller), expected)
    }

    func testSuccessiveUpdatesReachTheStableController() {
        let source = FakeRuntimeSource()
        let controller = MainViewControllerKt.createDiagnosticController(source: source)
        controller.load()
        waitForKind(controller, "content")
        waitForContent(controller, "first")
        source.value = "second"
        controller.load()
        waitForContent(controller, "second")
    }

    func testUnavailableRuntimeShowsSanitizedError() {
        let source = FakeRuntimeSource()
        source.value = nil
        let controller = MainViewControllerKt.createDiagnosticController(source: source)
        controller.load()
        waitForKind(controller, "error")
    }

    func testCancelAllowsAnExplicitReload() {
        let source = FakeRuntimeSource()
        let controller = MainViewControllerKt.createDiagnosticController(source: source)
        controller.load()
        waitForContent(controller, "first")
        controller.cancel()
        source.value = "second"
        controller.load()
        waitForContent(controller, "second")
    }

    func testDisposalIsTerminal() {
        let source = FakeRuntimeSource()
        let controller = MainViewControllerKt.createDiagnosticController(source: source)
        controller.dispose()
        controller.load()
        XCTAssertEqual(
            MainViewControllerKt.diagnosticPhaseKind(controller: controller), "loading")
    }
}
