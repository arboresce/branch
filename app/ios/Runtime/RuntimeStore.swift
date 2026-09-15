import Combine
import Foundation

actor RuntimeClient {
    private let runtime = BranchRuntime()
    func snapshot() throws -> String { try runtime.snapshotJson() }
    deinit { try? runtime.shutdown() }
}

@MainActor
final class RuntimeStore: ObservableObject {
    @Published private(set) var snapshot: String?
    private let client = RuntimeClient()
    func load() async {
        guard snapshot == nil else { return }
        do { snapshot = try await client.snapshot() } catch {
            snapshot = "{\"error\": \"runtime_unavailable\"}"
        }
    }
}
