import XCTest

@testable import Branch

final class RuntimeTests: XCTestCase {
    func testNativeSnapshotAndShutdown() throws {
        XCTAssertEqual(
            Bundle.main.object(forInfoDictionaryKey: "CFBundleDisplayName") as? String, "branch")
        let icons = try XCTUnwrap(
            Bundle.main.object(forInfoDictionaryKey: "CFBundleIcons") as? [String: Any])
        let primary = try XCTUnwrap(icons["CFBundlePrimaryIcon"] as? [String: Any])
        XCTAssertEqual(primary["CFBundleIconName"] as? String, "AppIcon")
        let runtime = BranchRuntime()
        let snapshot = try runtime.snapshotJson()
        let json = try XCTUnwrap(
            JSONSerialization.jsonObject(with: Data(snapshot.utf8)) as? [String: Any])
        XCTAssertEqual(json["schema_version"] as? Int, 1)
        let metadata = try XCTUnwrap(json["runtime"] as? [String: Any])
        XCTAssertEqual(metadata["os"] as? String, "ios")
        XCTAssertEqual(metadata["name"] as? String, "branch-by-arboresce")
        XCTAssertTrue((metadata["rustc"] as? String)?.hasPrefix("rustc ") == true)
        try runtime.shutdown()
        XCTAssertThrowsError(try runtime.snapshotJson())
    }
}
