import Foundation

/// Groups all service protocol references for dependency injection.
/// Created once at the app entry point via `production()` and passed through the environment.
@MainActor
struct ServiceContainer {
    let apiService: ClaudeAPIServiceProtocol
    let keychainService: KeychainServiceProtocol
    let clipboardService: ClipboardServiceProtocol
    var hotkeyService: HotkeyServiceProtocol
    let textSelectionService: TextSelectionServiceProtocol
    let screenCaptureService: ScreenCaptureServiceProtocol

    /// Production configuration with real service implementations.
    static func production() -> ServiceContainer {
        let clipboard = ClipboardService()
        return ServiceContainer(
            apiService: ClaudeAPIService(),
            keychainService: KeychainService(),
            clipboardService: clipboard,
            hotkeyService: HotkeyService(),
            textSelectionService: TextSelectionService(clipboard: clipboard),
            screenCaptureService: ScreenCaptureService()
        )
    }
}
