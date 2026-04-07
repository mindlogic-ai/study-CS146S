import Foundation

/// Abstracts secure credential storage (Keychain on macOS).
protocol KeychainServiceProtocol: Sendable {

    /// Save an API key to secure storage, replacing any existing value.
    /// - Returns: `true` if the key was saved successfully.
    @discardableResult
    func save(apiKey: String) -> Bool

    /// Load the stored API key.
    /// - Returns: The API key string, or `nil` if none is stored.
    func load() -> String?

    /// Delete the stored API key.
    /// - Returns: `true` if deletion succeeded or key did not exist.
    @discardableResult
    func delete() -> Bool

    /// Whether an API key currently exists in storage.
    var hasKey: Bool { get }

    /// A masked representation of the stored key for UI display.
    /// - Returns: e.g. "sk-ant-...xxxx", or `nil` if no key is stored.
    func maskedKey() -> String?
}
