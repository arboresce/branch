import BranchCatalogUI
import XCTest

final class CatalogTests: XCTestCase {
    func testFixedFixtureTitlesAreDeterministic() {
        XCTAssertEqual(
            CatalogBridgeKt.catalogItemTitles(),
            [
                "Catalog Item 1", "Catalog Item 2", "Catalog Item 3", "Catalog Item 4",
                "Catalog Item 5",
            ]
        )
    }
}
