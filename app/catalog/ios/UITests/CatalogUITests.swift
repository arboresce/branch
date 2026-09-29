import XCTest

final class CatalogUITests: XCTestCase {
    private func reveal(
        _ app: XCUIApplication,
        _ element: XCUIElement,
        attempts: Int = 8
    ) -> Bool {
        for _ in 0..<attempts {
            if element.exists {
                return true
            }
            app.swipeUp()
        }
        return element.exists
    }

    private func element(_ app: XCUIApplication, _ identifier: String) -> XCUIElement {
        app.descendants(matching: .any).matching(identifier: identifier).firstMatch
    }

    private func revealHittable(
        _ app: XCUIApplication,
        _ element: XCUIElement,
        attempts: Int = 8
    ) -> Bool {
        for _ in 0..<attempts {
            if element.isHittable {
                return true
            }
            app.swipeUp()
        }
        return element.isHittable
    }

    func testCatalogRendersFixedFixtures() {
        let app = XCUIApplication()
        app.launch()
        XCTAssertTrue(element(app, "catalog-title").waitForExistence(timeout: 30))
        XCTAssertTrue(reveal(app, element(app, "catalog-item-1")))
    }

    func testCatalogOnlyResourceRenders() {
        let app = XCUIApplication()
        app.launch()
        XCTAssertTrue(element(app, "catalog-resource").waitForExistence(timeout: 30))
    }

    func testGlassProbeRendersLiveSurfaceAndBothFallbacks() {
        let app = XCUIApplication()
        app.launch()
        for tag in ["glass-surface", "glass-fallback-capability", "glass-fallback-effects"] {
            XCTAssertTrue(reveal(app, element(app, tag)), tag)
        }
        let list = element(app, "catalog-list")
        for step in 0..<4 {
            let attachment = XCTAttachment(screenshot: XCUIScreen.main.screenshot())
            attachment.name = "glass-scroll-\(step)"
            attachment.lifetime = .keepAlways
            add(attachment)
            list.swipeUp()
        }
    }

    func testNavigationProbeTransitionsBetweenTwoEntries() {
        let app = XCUIApplication()
        app.launch()
        let push = element(app, "nav3-push")
        XCTAssertTrue(revealHittable(app, push))
        push.tap()
        XCTAssertTrue(element(app, "nav3-detail").waitForExistence(timeout: 30))
    }

    func testImageProbeResolvesDeterministicSuccessAndError() {
        let app = XCUIApplication()
        app.launch()
        XCTAssertTrue(reveal(app, element(app, "image-error")))
        XCTAssertTrue(reveal(app, element(app, "image-success")))
    }

    func testDiagnosticUpdatesInPlaceAndResumesAfterBackground() {
        let app = XCUIApplication()
        app.launch()
        let snapshot = element(app, "runtime-snapshot")
        XCTAssertTrue(snapshot.waitForExistence(timeout: 30))
        let next = element(app, "diagnostic-next")
        XCTAssertTrue(next.waitForExistence(timeout: 30))
        next.tap()
        let updated = XCTNSPredicateExpectation(
            predicate: NSPredicate(format: "label CONTAINS %@", "\"revision\":1"),
            object: snapshot)
        XCTAssertEqual(XCTWaiter().wait(for: [updated], timeout: 15), .completed)
        XCUIDevice.shared.press(.home)
        app.activate()
        let resumed = element(app, "runtime-snapshot")
        XCTAssertTrue(resumed.waitForExistence(timeout: 30))
        XCTAssertTrue(resumed.label.contains("\"revision\""))
    }
}
