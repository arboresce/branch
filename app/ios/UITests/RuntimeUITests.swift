import XCTest

final class RuntimeUITests: XCTestCase {
    func testHomeDisplaysRustSnapshot() {
        let app = XCUIApplication()
        app.launch()
        let snapshot = app.descendants(matching: .any).matching(identifier: "runtime-snapshot")
            .firstMatch
        XCTAssertTrue(snapshot.waitForExistence(timeout: 30))
        XCTAssertTrue(snapshot.label.contains("branch-by-arboresce"))
        XCTAssertTrue(snapshot.label.contains("schema_version"))
        XCTAssertTrue(snapshot.label.contains("rustc"))
    }

    func testHomeResumesWithVisibleContentAfterBackground() {
        let app = XCUIApplication()
        app.launch()
        let snapshot = app.descendants(matching: .any).matching(identifier: "runtime-snapshot")
            .firstMatch
        XCTAssertTrue(snapshot.waitForExistence(timeout: 30))
        XCUIDevice.shared.press(.home)
        app.activate()
        let resumed = app.descendants(matching: .any).matching(identifier: "runtime-snapshot")
            .firstMatch
        XCTAssertTrue(resumed.waitForExistence(timeout: 30))
        XCTAssertTrue(resumed.label.contains("schema_version"))
    }
}
