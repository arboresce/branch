import XCTest

final class CatalogUITests: XCTestCase {
    func testCatalogRendersFixedFixtures() {
        let app = XCUIApplication()
        app.launch()
        let title = app.descendants(matching: .any).matching(identifier: "catalog-title").firstMatch
        XCTAssertTrue(title.waitForExistence(timeout: 30))
        let item = app.descendants(matching: .any).matching(identifier: "catalog-item-1").firstMatch
        XCTAssertTrue(item.waitForExistence(timeout: 30))
    }

    func testNavigationProbeTransitionsBetweenTwoEntries() {
        let app = XCUIApplication()
        app.launch()
        let push = app.descendants(matching: .any).matching(identifier: "nav3-push").firstMatch
        XCTAssertTrue(push.waitForExistence(timeout: 30))
        push.tap()
        let detail = app.descendants(matching: .any).matching(identifier: "nav3-detail").firstMatch
        XCTAssertTrue(detail.waitForExistence(timeout: 30))
    }

    func testImageProbeResolvesDeterministicSuccessAndError() {
        let app = XCUIApplication()
        app.launch()
        let error = app.descendants(matching: .any).matching(identifier: "image-error").firstMatch
        XCTAssertTrue(error.waitForExistence(timeout: 30))
        let success = app.descendants(matching: .any).matching(identifier: "image-success").firstMatch
        XCTAssertTrue(success.waitForExistence(timeout: 30))
    }
}
