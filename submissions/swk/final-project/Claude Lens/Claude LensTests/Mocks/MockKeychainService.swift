import Foundation
@testable import Claude_Lens

/// In-memory mock for KeychainServiceProtocol.
/// Uses a dictionary instead of the Security framework — safe for unit tests.
final class MockKeychainService: KeychainServiceProtocol, @unchecked Sendable {

    // --- Storage ---
    private var storedKey: String?

    // --- Configuration ---
    var saveShouldSucceed: Bool = true
    var deleteShouldSucceed: Bool = true

    // --- Call Tracking ---
    var saveCallCount = 0
    var loadCallCount = 0
    var deleteCallCount = 0
    var maskedKeyCallCount = 0

    init(preloadedKey: String? = nil) {
        storedKey = preloadedKey
    }

    @discardableResult
    func save(apiKey: String) -> Bool {
        saveCallCount += 1
        guard saveShouldSucceed else { return false }
        storedKey = apiKey
        return true
    }

    func load() -> String? {
        loadCallCount += 1
        return storedKey
    }

    @discardableResult
    func delete() -> Bool {
        deleteCallCount += 1
        storedKey = nil
        return deleteShouldSucceed
    }

    var hasKey: Bool {
        storedKey != nil
    }

    func maskedKey() -> String? {
        maskedKeyCallCount += 1
        guard let key = storedKey else { return nil }
        if key.count > 12 {
            return String(key.prefix(7)) + "..." + String(key.suffix(4))
        }
        return "••••••••"
    }
}
