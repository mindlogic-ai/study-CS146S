import Foundation
import Security

/// Concrete implementation of KeychainServiceProtocol.
/// Thread-safe Security framework calls — not restricted to @MainActor.
final class KeychainService: KeychainServiceProtocol {

    private let service = "com.claudelens.apikey"
    private let account = "anthropic-api-key"

    init() {}

    @discardableResult
    func save(apiKey: String) -> Bool {
        guard let data = apiKey.data(using: .utf8) else { return false }
        delete()
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrService as String: service,
            kSecAttrAccount as String: account,
            kSecValueData as String: data,
            kSecAttrAccessible as String: kSecAttrAccessibleWhenUnlockedThisDeviceOnly
        ]
        let status = SecItemAdd(query as CFDictionary, nil)
        return status == errSecSuccess
    }

    func load() -> String? {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrService as String: service,
            kSecAttrAccount as String: account,
            kSecReturnData as String: true,
            kSecMatchLimit as String: kSecMatchLimitOne
        ]
        var result: AnyObject?
        let status = SecItemCopyMatching(query as CFDictionary, &result)
        guard status == errSecSuccess, let data = result as? Data else { return nil }
        return String(data: data, encoding: .utf8)
    }

    @discardableResult
    func delete() -> Bool {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrService as String: service,
            kSecAttrAccount as String: account
        ]
        let status = SecItemDelete(query as CFDictionary)
        return status == errSecSuccess || status == errSecItemNotFound
    }

    var hasKey: Bool {
        load() != nil
    }

    func maskedKey() -> String? {
        guard let key = load() else { return nil }
        if key.count > 12 {
            return String(key.prefix(7)) + "..." + String(key.suffix(4))
        }
        return "••••••••"
    }
}
