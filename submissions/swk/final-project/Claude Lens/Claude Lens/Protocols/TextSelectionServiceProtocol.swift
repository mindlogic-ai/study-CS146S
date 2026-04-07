import Foundation

/// Abstracts the capture of currently-selected text from the active application.
/// Requires macOS Accessibility permission.
@MainActor
protocol TextSelectionServiceProtocol {

    /// Capture the currently selected text in the frontmost application.
    ///
    /// Implementation:
    /// 1. Backup clipboard
    /// 2. Simulate ⌘+C via CGEvent
    /// 3. Wait for clipboard update (~80ms)
    /// 4. Read text from clipboard
    /// 5. Restore original clipboard
    ///
    /// - Returns: The selected text, or `nil` if nothing was selected
    ///   or accessibility permission is not granted.
    func captureSelectedText() async -> String?

    /// Whether the Accessibility permission has been granted by the user.
    var isAccessibilityGranted: Bool { get }

    /// Prompt the user to grant Accessibility permission via System Settings.
    func requestAccessibility()
}
