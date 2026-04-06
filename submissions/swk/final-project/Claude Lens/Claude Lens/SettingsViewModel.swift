import Foundation
import AppKit

@MainActor
@Observable
final class SettingsViewModel {
    var apiKeyInput = ""
    var isValidating = false
    var validationResult: Bool?

    var customSystemPrompt: String {
        get { UserDefaults.standard.string(forKey: "customSystemPrompt") ?? "" }
        set { UserDefaults.standard.set(newValue, forKey: "customSystemPrompt") }
    }

    // --- Dependencies ---
    private let apiService: ClaudeAPIServiceProtocol
    private let keychainService: KeychainServiceProtocol

    init(
        apiService: ClaudeAPIServiceProtocol,
        keychainService: KeychainServiceProtocol
    ) {
        self.apiService = apiService
        self.keychainService = keychainService
    }

    var maskedKey: String {
        keychainService.maskedKey() ?? "Not set"
    }

    var hasAPIKey: Bool {
        keychainService.hasKey
    }

    func saveAPIKey() async -> Bool {
        let key = apiKeyInput.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !key.isEmpty else { return false }

        isValidating = true
        let isValid = await apiService.validateAPIKey(key)
        isValidating = false

        if isValid {
            let saved = keychainService.save(apiKey: key)
            validationResult = saved
            apiKeyInput = ""
            return saved
        } else {
            validationResult = false
            return false
        }
    }

    func deleteAPIKey() {
        keychainService.delete()
        validationResult = nil
    }

    // Permission checks are direct OS calls (not worth abstracting behind a protocol)
    var isAccessibilityGranted: Bool {
        AXIsProcessTrusted()
    }

    var isScreenCaptureGranted: Bool {
        CGPreflightScreenCaptureAccess()
    }
}
