import Foundation

/// Identifies a registered hotkey for unregistration.
struct HotkeyRegistration: Sendable {
    let id: UInt32
}

/// Abstracts global hotkey registration using the Carbon Event API.
/// Must be called on @MainActor (Carbon events dispatch on the main thread).
@MainActor
protocol HotkeyServiceProtocol {

    /// Register all configured global hotkeys.
    /// Sets up the Carbon event handler and registers individual key combos.
    func register()

    /// Unregister all global hotkeys and tear down the event handler.
    func unregister()

    /// Callback invoked when the text capture hotkey (default: ⌘+⇧+L) is pressed.
    var onTextCapture: (() -> Void)? { get set }

    /// Callback invoked when the screenshot capture hotkey (default: ⌘+⇧+K) is pressed.
    var onScreenshotCapture: (() -> Void)? { get set }
}
