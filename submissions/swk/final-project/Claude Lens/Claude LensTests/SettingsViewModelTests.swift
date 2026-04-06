import Foundation
import Testing
@testable import Claude_Lens

@Suite("SettingsViewModel")
@MainActor
struct SettingsViewModelTests {

    // MARK: - Helpers

    private func makeViewModel(
        preloadedKey: String? = nil,
        validateKeyResult: Bool = true
    ) -> (SettingsViewModel, MockClaudeAPIService, MockKeychainService) {
        let api = MockClaudeAPIService()
        api.validateKeyResult = validateKeyResult
        let keychain = MockKeychainService(preloadedKey: preloadedKey)
        let vm = SettingsViewModel(apiService: api, keychainService: keychain)
        return (vm, api, keychain)
    }

    // MARK: - hasAPIKey

    @Test("hasAPIKey is false when keychain is empty")
    func hasAPIKeyFalseWhenEmpty() {
        // Given
        let (vm, _, _) = makeViewModel(preloadedKey: nil)

        // Then
        #expect(vm.hasAPIKey == false)
    }

    @Test("hasAPIKey is true when key exists in keychain")
    func hasAPIKeyTrueWhenPresent() {
        // Given
        let (vm, _, _) = makeViewModel(preloadedKey: "sk-ant-test1234567890")

        // Then
        #expect(vm.hasAPIKey == true)
    }

    // MARK: - maskedKey

    @Test("maskedKey returns 'Not set' when no key stored")
    func maskedKeyNotSetWhenEmpty() {
        // Given
        let (vm, _, _) = makeViewModel(preloadedKey: nil)

        // Then
        #expect(vm.maskedKey == "Not set")
    }

    @Test("maskedKey returns masked string when key is stored")
    func maskedKeyReturnsMaskedValue() {
        // Given
        let (vm, _, _) = makeViewModel(preloadedKey: "sk-ant-api03-longkeyvalue1234")

        // Then
        let masked = vm.maskedKey
        #expect(masked != "Not set")
        #expect(!masked.isEmpty)
        // Masked form should contain "..." separator
        #expect(masked.contains("..."))
    }

    @Test("maskedKey shows first 7 chars and last 4 chars for long keys")
    func maskedKeyFormat() {
        // Given — a key longer than 12 chars
        let key = "sk-ant-ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        let (vm, _, _) = makeViewModel(preloadedKey: key)

        // When
        let masked = vm.maskedKey

        // Then
        #expect(masked.hasPrefix("sk-ant-"))
        #expect(masked.hasSuffix("WXYZ"))
    }

    // MARK: - saveAPIKey — valid key

    @Test("saveAPIKey validates key and saves to keychain on success")
    func saveAPIKeySuccess() async {
        // Given
        let (vm, api, keychain) = makeViewModel(validateKeyResult: true)
        vm.apiKeyInput = "sk-ant-valid-key-here"

        // When
        let result = await vm.saveAPIKey()

        // Then
        #expect(result == true)
        #expect(api.validateAPIKeyCallCount == 1)
        #expect(api.lastValidatedKey == "sk-ant-valid-key-here")
        #expect(keychain.saveCallCount == 1)
        #expect(keychain.hasKey == true)
    }

    @Test("saveAPIKey clears apiKeyInput after successful save")
    func saveAPIKeyClearsInput() async {
        // Given
        let (vm, _, _) = makeViewModel(validateKeyResult: true)
        vm.apiKeyInput = "sk-ant-valid-key-here"

        // When
        _ = await vm.saveAPIKey()

        // Then
        #expect(vm.apiKeyInput == "")
    }

    @Test("saveAPIKey sets validationResult to true on success")
    func saveAPIKeySetsValidationResultTrue() async {
        // Given
        let (vm, _, _) = makeViewModel(validateKeyResult: true)
        vm.apiKeyInput = "sk-ant-valid-key"

        // When
        _ = await vm.saveAPIKey()

        // Then
        #expect(vm.validationResult == true)
    }

    @Test("saveAPIKey toggles isValidating to false after completion")
    func saveAPIKeyIsValidatingFalseAfter() async {
        // Given
        let (vm, _, _) = makeViewModel(validateKeyResult: true)
        vm.apiKeyInput = "sk-ant-valid-key"

        // When
        _ = await vm.saveAPIKey()

        // Then
        #expect(vm.isValidating == false)
    }

    // MARK: - saveAPIKey — invalid key

    @Test("saveAPIKey does not save to keychain when validation fails")
    func saveAPIKeyDoesNotSaveOnValidationFailure() async {
        // Given
        let (vm, api, keychain) = makeViewModel(validateKeyResult: false)
        vm.apiKeyInput = "sk-ant-bad-key"

        // When
        let result = await vm.saveAPIKey()

        // Then
        #expect(result == false)
        #expect(api.validateAPIKeyCallCount == 1)
        #expect(keychain.saveCallCount == 0)
        #expect(keychain.hasKey == false)
    }

    @Test("saveAPIKey sets validationResult to false when validation fails")
    func saveAPIKeySetsValidationResultFalse() async {
        // Given
        let (vm, _, _) = makeViewModel(validateKeyResult: false)
        vm.apiKeyInput = "sk-ant-bad-key"

        // When
        _ = await vm.saveAPIKey()

        // Then
        #expect(vm.validationResult == false)
    }

    // MARK: - saveAPIKey — empty input

    @Test("saveAPIKey returns false and skips validation for empty input")
    func saveAPIKeyEmptyInputReturnsFalse() async {
        // Given
        let (vm, api, _) = makeViewModel()
        vm.apiKeyInput = "   " // whitespace only

        // When
        let result = await vm.saveAPIKey()

        // Then
        #expect(result == false)
        #expect(api.validateAPIKeyCallCount == 0)
    }

    // MARK: - deleteAPIKey

    @Test("deleteAPIKey removes key from keychain")
    func deleteAPIKeyRemovesKey() {
        // Given
        let (vm, _, keychain) = makeViewModel(preloadedKey: "sk-ant-existingkey")
        #expect(vm.hasAPIKey == true)

        // When
        vm.deleteAPIKey()

        // Then
        #expect(keychain.deleteCallCount == 1)
        #expect(vm.hasAPIKey == false)
    }

    @Test("deleteAPIKey resets validationResult to nil")
    func deleteAPIKeyResetsValidationResult() {
        // Given
        let (vm, _, _) = makeViewModel(preloadedKey: "sk-ant-existingkey")
        vm.validationResult = true

        // When
        vm.deleteAPIKey()

        // Then
        #expect(vm.validationResult == nil)
    }
}
