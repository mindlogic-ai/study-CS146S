import AppKit
import Foundation

/// Concrete implementation of TextSelectionServiceProtocol.
/// @MainActor because CGEvent simulation and clipboard access must be on the main thread.
@MainActor
final class TextSelectionService: TextSelectionServiceProtocol {

    private let clipboard: ClipboardServiceProtocol

    init(clipboard: ClipboardServiceProtocol) {
        self.clipboard = clipboard
    }

    func captureSelectedText() async -> String? {
        let backupData = clipboard.backup()

        simulateCopy()
        try? await Task.sleep(for: .milliseconds(80))

        let captured = clipboard.readText()
        clipboard.restore(from: backupData)

        return captured
    }

    private func simulateCopy() {
        let source = CGEventSource(stateID: .hidSystemState)
        let keyDown = CGEvent(keyboardEventSource: source, virtualKey: 0x08, keyDown: true)
        keyDown?.flags = .maskCommand
        keyDown?.post(tap: .cghidEventTap)

        let keyUp = CGEvent(keyboardEventSource: source, virtualKey: 0x08, keyDown: false)
        keyUp?.flags = .maskCommand
        keyUp?.post(tap: .cghidEventTap)
    }

    var isAccessibilityGranted: Bool {
        AXIsProcessTrusted()
    }

    func requestAccessibility() {
        let options = [kAXTrustedCheckOptionPrompt.takeUnretainedValue(): true] as CFDictionary
        AXIsProcessTrustedWithOptions(options)
    }
}
