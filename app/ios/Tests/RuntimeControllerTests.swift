import BranchUI
import XCTest

private final class FakeRuntimeSource: AppRuntimeSource {
    var value: String? = "first"
    var calls = 0

    func snapshot() -> String? {
        calls += 1
        return value
    }
}

private final class BlockingRuntimeSource: AppRuntimeSource {
    private let semaphore = DispatchSemaphore(value: 0)
    private let lock = NSLock()
    private var count = 0

    var calls: Int {
        lock.lock()
        defer { lock.unlock() }
        return count
    }

    func snapshot() -> String? {
        lock.lock()
        count += 1
        lock.unlock()
        semaphore.wait()
        return "ok"
    }

    func release() {
        semaphore.signal()
    }
}

final class RuntimeControllerTests: XCTestCase {
    private func waitFor(
        _ condition: @escaping () -> Bool,
        timeout: TimeInterval = 5
    ) {
        let deadline = Date().addingTimeInterval(timeout)
        while Date() < deadline, !condition() {
            RunLoop.current.run(until: Date().addingTimeInterval(0.02))
        }
        XCTAssertTrue(condition())
    }

    private func waitForKind(
        _ controller: AppRuntimeController,
        _ expected: String
    ) {
        waitFor { MainViewControllerKt.diagnosticPhaseKind(controller: controller) == expected }
    }

    private func waitForContent(
        _ controller: AppRuntimeController,
        _ expected: String
    ) {
        waitFor { MainViewControllerKt.diagnosticContent(controller: controller) == expected }
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

    func testPauseThenResumeLoadsExactlyOnce() {
        let source = FakeRuntimeSource()
        let controller = MainViewControllerKt.createDiagnosticController(source: source)
        controller.load()
        waitForContent(controller, "first")
        controller.cancel()
        controller.load()
        waitForContent(controller, "first")
        controller.cancel()
        controller.load()
        waitForContent(controller, "first")
        XCTAssertEqual(source.calls, 3)
        controller.dispose()
    }

    func testCancelWhileBlockedThenResumeDoesNotOverlapOrDuplicate() {
        let source = BlockingRuntimeSource()
        let controller = MainViewControllerKt.createDiagnosticController(source: source)
        controller.load()
        waitFor { source.calls == 1 }
        controller.cancel()
        controller.load()
        RunLoop.current.run(until: Date().addingTimeInterval(0.3))
        XCTAssertEqual(source.calls, 1, "a second call must not start while the first is in flight")
        source.release()
        waitFor { source.calls == 2 }
        controller.load()
        RunLoop.current.run(until: Date().addingTimeInterval(0.3))
        XCTAssertEqual(source.calls, 2, "an active load must not start a duplicate call")
        source.release()
        waitForContent(controller, "ok")
        controller.dispose()
        XCTAssertEqual(source.calls, 2)
    }

    func testDisposalIsTerminal() {
        let source = FakeRuntimeSource()
        let controller = MainViewControllerKt.createDiagnosticController(source: source)
        controller.dispose()
        controller.load()
        XCTAssertEqual(
            MainViewControllerKt.diagnosticPhaseKind(controller: controller), "loading")
        XCTAssertEqual(source.calls, 0)
    }

    func testDisposeWhileBlockedRejectsCompletionAndLaterLoads() {
        let source = BlockingRuntimeSource()
        let controller = MainViewControllerKt.createDiagnosticController(source: source)
        controller.load()
        waitFor { source.calls == 1 }
        controller.dispose()
        source.release()
        RunLoop.current.run(until: Date().addingTimeInterval(0.3))
        controller.load()
        RunLoop.current.run(until: Date().addingTimeInterval(0.3))
        XCTAssertEqual(source.calls, 1)
        XCTAssertEqual(
            MainViewControllerKt.diagnosticPhaseKind(controller: controller), "loading")
    }
}
