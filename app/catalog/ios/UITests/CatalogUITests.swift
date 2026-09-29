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
}
